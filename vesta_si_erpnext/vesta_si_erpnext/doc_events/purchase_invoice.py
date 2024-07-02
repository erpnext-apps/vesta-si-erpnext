import frappe
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

def get_advance_entries(self):
	res = self.get_advance_entries(
			include_unallocated=not cint(self.get("only_include_allocated_payments"))
		)
	if res and not self.allocate_advances_automatically:
		if not len(self.advances):
			frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(self.supplier))