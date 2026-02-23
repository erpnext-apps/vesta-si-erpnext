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
from frappe.desk.form.load import get_attachments
from erpnext.accounts.utils import get_outstanding_invoices


def set_due_date_after_submit(self, method):
    if self.docstatus == 1:
        if self.payment_schedule:
            frappe.db.set_value("Purchase Invoice", self.name, 'due_date', self.payment_schedule[-1].due_date)
            self.reload()

def validate(self, method):
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
				
	# frappe.throw(str(data))

	final_data = []
	for row in data:
		if not row.voucher_no in ["ACC-PINV-2024-00250-1", "ACC-PINV-2024-00251-1"]:
			final_data.append(row)
	# if len(final_data):
	# 	message = "Debit Note and Payment Entry available against this supplier <b>{0}</b><br>".format(get_link_to_form("Supplier",self.supplier))
	# 	message +="First reconcile those entry, reference available as mentioned below"
	# 	message += "<br><br>"
	# 	message += """<table width='100%'>"""
	# 	for row in data:
	# 		message += "<tr><td>{0}</td><td>{1} {2}</td></tr>".format(get_link_to_form(row.voucher_type, row.voucher_no),self.currency, row.outstanding_amount)
	# 	message += "</table>"
		
	# 	frappe.msgprint(message)
		
	if not self.is_return:
		set_exchange_rate(self, method)
		self.validate()
		check_item_level_changes(self) 
	validate_currency(self) #Do not deploy

def after_insert(self, method):
    get_attachment_from_po(self)

import os
import frappe
from frappe.utils import get_site_path


def file_exists_on_disk(file_url):
	if not file_url:
		return False

	file_url = file_url.lstrip("/")
	file_path = get_site_path(file_url)
	return os.path.exists(file_path)


import os
import frappe
from frappe.utils import get_site_path


def file_exists_on_disk(file_url):
	if not file_url:
		return False

	file_url = file_url.lstrip("/")
	file_path = get_site_path(file_url)
	return os.path.exists(file_path)


def get_attachment_from_po(self):
	if not self.items or not self.items[0].get("purchase_receipt"):
		return

	attached_files = get_attachments(
		"Purchase Receipt",
		self.items[0].get("purchase_receipt")
	)

	for file_row in attached_files:
		# 1️⃣ Check if already attached to this Purchase Invoice
		exists_in_pi = frappe.db.exists(
			"File",
			{
				"file_url": file_row.file_url,
				"attached_to_doctype": "Purchase Invoice",
				"attached_to_name": self.name,
			},
		)

		# 2️⃣ If record exists AND file exists physically → skip
		if exists_in_pi and file_exists_on_disk(file_row.file_url):
			continue

		try:
			new_file = frappe.get_doc({
				"doctype": "File",
				"file_name": file_row.file_name,
				"file_url": file_row.file_url,
				"attached_to_doctype": "Purchase Invoice",
				"attached_to_name": self.name,
			})
			new_file.insert(ignore_permissions=True)
		except:
			frappe.log_error("File is not exists", self.name)



def get_advance_entries(self):
    res = self.get_advance_entries(
            include_unallocated=not cint(self.get("only_include_allocated_payments"))
        )
    if res and not self.allocate_advances_automatically:
        if not len(self.advances):
            frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(self.supplier))

#validate the currency based on supplier payment type 
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

# Not allow to change item code , qty and not allow to add row
def check_item_level_changes(self):
	buying_setting =  frappe.get_doc("Buying Settings")
	allow_extra_item =[ row.item for row in buying_setting.allow_extra_item]
	po_flage = False
	for row in self.items:
		if row.purchase_receipt:
			po_flage = True
			po_data = frappe.db.sql(f"""
						Select item_code, name, qty, base_amount
						From `tabPurchase Order Item`
						Where name = '{row.po_detail}'
			""", as_dict = 1)
			if not po_data:
				continue
			item_allownce_percentage = 0
			item_allownce =0

			allow_overbill_by = frappe.db.get_value("Item", row.item_code, "allow_overbill_by")
			if (allow_overbill_by == "Don't Allow Overbilling") and row.base_amount > po_data[0].get("base_amount") and self.currency == "SEK":
				frappe.throw(f"Row #{row.idx} : Not allow to change a rate for item <b>{row.item_code}</b>")

			if allow_overbill_by == "Amount":
				item_allownce = frappe.db.get_value("Item", row.item_code, "overbill_allow_by_amount")
			if allow_overbill_by == "Percentage":
				item_allownce_percentage = frappe.db.get_value("Item", row.item_code, "over_billing_allowance")
				if item_allownce_percentage:
					item_allownce = po_data[0].get("base_amount") * flt(item_allownce_percentage) / 100
			
			if not item_allownce and not self.is_new() and (row.base_amount - po_data[0].get("base_amount")) > item_allownce and self.currency == "SEK":
				frappe.throw(f"Row #{row.idx} : Overbilling not allow for Item <b>{row.item_code}</b>")
			# if row.qty != po_data[0].get("qty") and frappe.db.get_value("Item", row.item_code, "is_stock_item"):
			# 	frappe.throw(f"Row #{row.idx} : Accepted Qty should be same as purchase receipt quantiy")
			if item_allownce > 0  and (row.base_amount - po_data[0].get("base_amount")) > item_allownce and self.currency == "SEK":
				if not item_allownce_percentage:
					frappe.throw(f"Row #{row.idx} : Overbilling is not allowed beyond {item_allownce} SEK.")
				else:
					frappe.throw(f"Row #{row.idx} : Overbilling is not allowed beyond {item_allownce} SEK ({item_allownce_percentage} %) .")
		if po_flage and not row.purchase_order and row.item_code not in allow_extra_item:
			frappe.throw(f"Row #{row.idx}: Not Allow to add Item, It should be available in purchase order")
