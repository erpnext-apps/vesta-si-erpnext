import frappe
from frappe import _
from frappe.utils import get_link_to_form, comma_and, flt
from erpnext.accounts.doctype.payment_entry.payment_entry import get_negative_outstanding_invoices
from frappe.utils import (
	add_days,
	add_months,
	cint,
	comma_and,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
)


def set_due_date_after_submit(self, method):
	if self.docstatus == 1:
		if self.payment_schedule:
			frappe.db.set_value("Purchase Invoice", self.name, 'due_date', self.payment_schedule[-1].due_date)
			self.reload()

def validate(self, method):
	# pass
	get_advance_entries(self)
	party_account_currency = frappe.db.get_value("Account", self.credit_to, 'account_currency')
	company_currency = frappe.db.get_value("Company", self.company, 'default_currency')
	data = get_negative_outstanding_invoices(
				"Supplier", 
				self.supplier, 
				self.credit_to, 
				party_account_currency, 
				company_currency,
				condition = '')
	if len(data):
		for row in data:
			message = "Debit Note and Payment Entry available against this supplier <b>{0}</b><br>".format(get_link_to_form("Supplier",self.supplier))
			message +="First reconcile those entry, reference available as mentioned below"
			message += "<br><br>"
			message += """<table width='100%'>"""
			for row in data:
				message += "<tr><td>{0}</td><td>{1} {2}</td></tr>".format(get_link_to_form(row.voucher_type, row.voucher_no),self.currency, row.outstanding_amount)
			message += "</table>"
			frappe.msgprint(message)
	validate_with_previous_doc(self)

def get_advance_entries(self):
	res = self.get_advance_entries(
			include_unallocated=not cint(self.get("only_include_allocated_payments"))
		)
	if res and not self.allocate_advances_automatically:
		if not len(self.advances):
			frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(self.supplier))

def on_submit(self, method):
	for row in self.items:
		is_stock_item = frappe.db.get_value("Item", row.item_code, "is_stock_item")
		if is_stock_item and row.purchase_receipt and row.pr_detail:
			pri_doc = frappe.get_doc("Purchase Receipt Item", row.pr_detail)
			if pri_doc.base_rate < row.base_rate:
				rate_diff = row.base_rate - pri_doc.base_rate
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Journal Entry"
				jv.posting_date = getdate()
				if row.expense_account in ["222501 - Goods & services received/Invoice received - non SKF - 9150", "222503 - Goods & services received/Invoice received - non SKF - 9150"]:
					jv.append("accounts", {
						"account" : row.expense_account,
						"credit_in_account_currency" : rate_diff
					})
				else:
					expense_account = frappe.db.get_value("Company", jv.company, "stock_received_but_not_billed")
					jv.append("accounts", {
						"account" : expense_account,
						"credit_in_account_currency" : rate_diff
					})
				tranfer_account = frappe.db.get_value("Company", jv.company, "custom_difference_account_purchase_receipt_and_purchase_invoice")
				jv.append("accounts", {
					"account" : tranfer_account,
					"debit_in_account_currency" : rate_diff
				})
				jv.cheque_no = self.name
				jv.cheque_date = getdate()
				jv.save()
				jv.submit()
				frappe.msgprint("The difference of <span style='color:red'>{0}</span> SEK between the purchase invoice {1} and the purchase receipt {2} is recorded in this journal entry {3}.".format(
					frappe.bold(rate_diff),
					get_link_to_form("Purchase Invoice",self.name),
					get_link_to_form("Purchase Receipt", row.purchase_receipt),
					get_link_to_form("Journal Entry",jv.name)
				))

def validate_with_previous_doc(self):
	if (
		not self.is_return
		and not self.is_internal_supplier
	):
		validate_rate_with_reference_doc(self,
			[
				["Purchase Order", "purchase_order", "po_detail"],
				["Purchase Receipt", "purchase_receipt", "pr_detail"],
			]
		)

def validate_rate_with_reference_doc(self, ref_details):
	if self.get("is_internal_supplier"):
		return

	buying_doctypes = ["Purchase Order", "Purchase Invoice", "Purchase Receipt"]

	stop_actions = []
	action = "Stop"
	for ref_dt, ref_dn_field, ref_link_field in ref_details:
		reference_names = [d.get(ref_link_field) for d in self.get("items") if d.get(ref_link_field)]
		reference_details = get_reference_details(self, reference_names, ref_dt + " Item")
		for d in self.get("items"):
			if not frappe.db.get_value("Item", d.item_code, "is_stock_item"):
				continue
			if d.get(ref_link_field):
				ref_rate = reference_details.get(d.get(ref_link_field))

				if abs(flt(d.rate - ref_rate, d.precision("rate"))) >= 0.01:
					if action == "Stop":
						# if role_allowed_to_override not in frappe.get_roles():
						stop_actions.append(
							_("Row #{0}: Rate must be same as {1}: {2} ({3} / {4})").format(
								d.idx, ref_dt, d.get(ref_dn_field), d.rate, ref_rate
							)
						)
					else:
						frappe.msgprint(
							_("Row #{0}: Rate must be same as {1}: {2} ({3} / {4})").format(
								d.idx, ref_dt, d.get(ref_dn_field), d.rate, ref_rate
							),
							title=_("Warning"),
							indicator="orange",
						)
	if stop_actions:
		frappe.throw(stop_actions, as_list=True)

def get_reference_details(self, reference_names, reference_doctype):
	return frappe._dict(
		frappe.get_all(
			reference_doctype,
			filters={"name": ("in", reference_names)},
			fields=["name", "rate"],
			as_list=1,
		)
	)