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