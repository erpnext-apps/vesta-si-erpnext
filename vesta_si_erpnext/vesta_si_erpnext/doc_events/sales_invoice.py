import frappe
from frappe.utils import getdate
from frappe.desk.form.load import get_attachments


@frappe.whitelist()
def get_items_from_stock_entry(stock_entry ):
    se =  frappe.parse_json(stock_entry)
    data = frappe.db.sql(f"""Select std.item_code, std.item_name , batch.batch_qty as qty , std.uom , std.basic_rate as rate, std.name as stock_entry_detail , 
                            std.batch_no , std.t_warehouse as warehouse , std.description
                            From `tabStock Entry` as se
                            Left Join `tabStock Entry Detail` as std ON std.parent = se.name and se.name = '{se.get("Stock Entry")}'
                            Left Join   `tabBatch` as batch ON std.batch_no = batch.name
                            Where std.is_finished_item = 1 and batch.batch_qty > 0 
                            """ , as_dict = 1)
                
    
    return data


# this function is applicable for purchase invoice and sales invoice only
def check_account_frozzen_date(self, method):
    if self.voucher_type == "Purchase Invoice":
        pi_frozen_date = frappe.db.get_value('Company', self.company, "custom_accounts_payable_purchase_invoice_frozen_till_date")
        if pi_frozen_date:
            if self.posting_date <= getdate(pi_frozen_date):
                frappe.throw(f"Accounting period till <b>{pi_frozen_date}</b> is closed. Select a date after <b>{pi_frozen_date}</b> in 'Posting Date' field.")
    if self.voucher_type == "Sales Invoice":
        si_frozen_date = frappe.db.get_value('Company', self.company, "custom_accounts_receivable_sales_invoice_frozen_till_date")
        if si_frozen_date:
            if self.posting_date <= getdate(si_frozen_date):
                frappe.throw(f"Accounting period till <b>{si_frozen_date}</b> is closed. Select a date after <b>{si_frozen_date}</b> in 'Posting Date' field.")


from erpnext.setup.utils import get_exchange_rate

def validate(self, method):
    if not self.is_return:
        set_exchange_rate(self, method)
        self.validate()


def set_exchange_rate(self,method):
    default_currency = frappe.db.get_value('Company', self.company, "default_currency")
    exchange_rate = get_exchange_rate(self.currency, default_currency, transaction_date = self.posting_date, args=None)
    self.conversion_rate = exchange_rate


def after_insert(self, method):
	get_attachment_from_po(self)

import os
import frappe
from frappe.desk.form.load import get_attachments
from frappe.utils import get_site_path


def file_exists_on_disk(file_url):
	if not file_url:
		return False

	file_url = file_url.lstrip("/")
	file_path = get_site_path(file_url)
	return os.path.exists(file_path)


def get_attachment_from_po(self):
	if not self.items or not self.items[0].get("sales_order"):
		return

	attached_files = get_attachments(
		"Sales Order",
		self.items[0].get("sales_order")
	)

	for file_row in attached_files:
		# 1️⃣ Check if already attached to this Sales Invoice
		exists_in_si = frappe.db.exists(
			"File",
			{
				"file_url": file_row.file_url,
				"attached_to_doctype": "Sales Invoice",
				"attached_to_name": self.name,
			},
		)

		# 2️⃣ If record exists AND file exists physically → skip
		if exists_in_si and file_exists_on_disk(file_row.file_url):
			continue

		# 3️⃣ Attach again if missing
		new_file = frappe.get_doc({
			"doctype": "File",
			"file_name": file_row.file_name,
			"file_url": file_row.file_url,
			"attached_to_doctype": "Sales Invoice",
			"attached_to_name": self.name,
		})
		new_file.insert(ignore_permissions=True)

