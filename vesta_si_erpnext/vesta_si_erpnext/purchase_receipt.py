# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.desk.form.load import get_attachments

def validate(self, method):
	if not self.is_return:
		set_exchange_rate(self)
		self.validate()
	check_same_rate_cycle(self)

def after_insert(self, method):
	get_attachment_from_po(self)



def get_attachment_from_po(self):
	if self.items[0].get("purchase_order"):
		attached_files = get_attachments("Purchase Order", self.items[0].get("purchase_order"))
		for row in attached_files:
			new_file = frappe.get_doc({ 
				"doctype" : "File",
				"file_name" : row.file_name,
				"file_url" : row.file_url,
				"attached_to_doctype" : "Purchase Receipt",
				"attached_to_name" : self.name
			})
			new_file.insert(ignore_permissions=True)

def link_supplier_bag_to_batch(doc, method=None):
	for item in doc.items:
		if item.get("supplier_bag_no") and item.get("batch_no"):
			frappe.db.set_value("Batch", item.batch_no, "supplier_bag_no", item.supplier_bag_no)

		# if item.get("quality_inspection") and item.get("batch_no"):
		# 	frappe.db.set_value("Quality Inspection", item.quality_inspection, "batch_no", item.batch_no)

def before_validate(doc, method):
	from vesta_si_erpnext.vesta_si_erpnext.putaway_rule import apply_putaway_rule

	doc.custom_apply_putaway_rule = 0
	if doc.apply_putaway_rule:
		doc.apply_putaway_rule = 0

		apply_putaway_rule(doc.doctype, doc.get("items"), doc.company)

		doc.custom_apply_putaway_rule = 1

def on_update(doc, method):
	if doc.custom_apply_putaway_rule:
		doc.db_set('apply_putaway_rule', 1)


#sent notification to Andrew if PO assign to him
def notification_to_assignee(self, method):
	if self.items[0].get("purchase_order"):
		doc = frappe.get_doc("Purchase Order", self.items[0].get("purchase_order"))
		if name := frappe.db.exists("ToDo", {"reference_type" : "Purchase Order", "reference_name": doc.name, "status" : ["!=", "Cancelled"]}):
			allocated_to = frappe.db.get_value("ToDo", name, "allocated_to")
			if allocated_to == "andre.awad@skf.com":
				notification_doc = frappe.get_doc("Notification", "Purchase Receipt notification")
				notification_doc.send(self)


from erpnext.setup.utils import get_exchange_rate


def set_exchange_rate(self):
	default_currency = frappe.db.get_value('Company', self.company, "default_currency")
	exchange_rate = get_exchange_rate(self.currency, default_currency, transaction_date = self.posting_date, args=None)
	self.conversion_rate = exchange_rate

def check_same_rate_cycle(self):
	same_rate_v = frappe.db.get_singles_value("Buying Settings", "enable_same_rate_validation" )
	if self.is_return:
		return
	if not same_rate_v:
		return
	for row in self.items:
		if row.purchase_order:
			po_details = frappe.db.sql(f"""
						Select item_code, qty, base_rate, rate
						From `tabPurchase Order Item`
						Where name = '{row.purchase_order_item}'
			""", as_dict = 1)
			# if po_details[0].get("qty") != row.qty and row.is_stock_item:
			# 	frappe.throw(f"Row #{row.idx}: Quantity not allow to change, It should be same as PO")
			if po_details[0].get("rate") != row.rate:
				frappe.throw(f"Row #{row.idx}: Rate not allow to change, It should be same as PO")


