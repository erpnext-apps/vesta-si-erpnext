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
	final_data = []
	for row in data:
		if not row.voucher_no in ["ACC-PINV-2024-00250-1", "ACC-PINV-2024-00251-1"]:
			final_data.append(row)
	if len(final_data):
		message = "Debit Note and Payment Entry available against this supplier <b>{0}</b><br>".format(get_link_to_form("Supplier",self.supplier))
		message +="First reconcile those entry, reference available as mentioned below"
		message += "<br><br>"
		message += """<table width='100%'>"""
		for row in data:
			message += "<tr><td>{0}</td><td>{1} {2}</td></tr>".format(get_link_to_form(row.voucher_type, row.voucher_no),self.currency, row.outstanding_amount)
		message += "</table>"
		
		frappe.msgprint(message)
		
	if not self.is_return:
		set_exchange_rate(self, method)
		self.validate()
	
	validate_currency(self) #Do not deploy

def get_advance_entries(self):
	res = self.get_advance_entries(
			include_unallocated=not cint(self.get("only_include_allocated_payments"))
		)
	if res and not self.allocate_advances_automatically:
		if not len(self.advances):
			frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(self.supplier))

#validate the currency based on supplier payment type (Do Not Deploy)
def validate_currency(self):
	payment_type = frappe.db.get_value("Supplier", self.supplier, "custom_payment_type")
	flags = False
	if payment_type == 'Domestic (Swedish) Payments (SEK)':
		invoice_currency = "SEK"
		if invoice_currency != self.currency:
			flags = True
	if payment_type == 'SEPA (EUR)':
		invoice_currency = "EUR"
		if invoice_currency != self.currency:
			flags = True
	if payment_type == 'Cross Border Payments (USD)':
		invoice_currency = "USD"
		if invoice_currency != self.currency:
			flags = True
	if payment_type == "Cross Border Payments (EUR)":
		invoice_currency = "EUR"
		if invoice_currency != self.currency:
			flags = True
	if payment_type in ['Domestic (Swedish) Payments (SEK)', 'SEPA (EUR)', 'Cross Border Payments (USD)', 'Cross Border Payments (EUR)']:
		if flags:
			message = f"Supplier Payment Type is <b>{payment_type}</b>, Invoice should be in <b>{invoice_currency}</b>.<br>   Or   <br>Kindly create a new supplier with billing currency <b>'{self.currency}'</b>."
			frappe.throw(message)
	
	
from erpnext.setup.utils import get_exchange_rate

def set_exchange_rate(self,method):
	default_currency = frappe.db.get_value('Company', self.company, "default_currency")
	exchange_rate = get_exchange_rate(self.currency, default_currency, transaction_date = self.posting_date, args=None)
	self.conversion_rate = exchange_rate

@frappe.whitelist()
def check_any_advance_payment(self):

	self = frappe._dict(json.loads(self))

	get_advance_entries_w(self)

	party_account_currency = frappe.db.get_value("Account", self.credit_to, 'account_currency')
	company_currency = frappe.db.get_value("Company", self.company, 'default_currency')
	data = get_negative_outstanding_invoices(
				"Supplier", 
				self.supplier, 
				self.credit_to, 
				party_account_currency, 
				company_currency,
				condition = '')
	final_data = []
	for row in data:
		if not row.voucher_no in ["ACC-PINV-2024-00250-1", "ACC-PINV-2024-00251-1"]:
			final_data.append(row)
	if len(final_data):
		message = "Debit Note and Payment Entry available against this supplier <b>{0}</b><br>".format(get_link_to_form("Supplier",self.supplier))
		message +="First reconcile those entry, reference available as mentioned below"
		message += "<br><br>"
		message += """<table width='100%'>"""
		for row in data:
			message += "<tr><td>{0}</td><td>{1} {2}</td></tr>".format(get_link_to_form(row.voucher_type, row.voucher_no),self.currency, row.outstanding_amount)
		message += "</table>"
		
		if message:
			return frappe.get_doc(row.voucher_type, row.voucher_no)

def get_advance_entries_w(self):
	doc = frappe.get_doc(self.doctype, self.name)
	res = doc.get_advance_entries(
			include_unallocated=not cint(doc.get("only_include_allocated_payments"))
		)
	if res and not doc.allocate_advances_automatically:
		if not len(doc.advances):
			frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(doc.supplier))