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