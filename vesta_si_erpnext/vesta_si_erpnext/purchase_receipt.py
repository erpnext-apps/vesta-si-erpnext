# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

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
	# pass
	if self.items[0].get("purchase_order"):
		doc = frappe.get_doc("Purchase Order", self.items[0].get("purchase_order"))
		if name := frappe.db.exists("ToDo", {"reference_type" : "Purchase Order", "reference_name": doc.name, "status" : ["!=", "Cancelled"]}):
			allocated_to = frappe.db.get_value("ToDo", name, "allocated_to")
			if allocated_to == "andre.awad@skf.com":
				notification_doc = frappe.get_doc("Notification", "Purchase Receipt notification")
				notification_doc.send(self)

