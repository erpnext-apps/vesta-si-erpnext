# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from erpnext.stock.doctype.batch.batch import make_batch

def link_supplier_bag_to_batch(doc, method=None):
	if (doc.purpose in ("Material Receipt", "Manufacture")):
		for item in doc.items:
			if item.get("supplier_bag_no") and item.get("batch_no"):
				frappe.db.set_value("Batch", item.batch_no, "supplier_bag_no", item.supplier_bag_no)

			# if item.get("quality_inspection") and item.get("batch_no"):
			# 	frappe.db.set_value("Quality Inspection", item.quality_inspection, "batch_no", item.batch_no)

def before_submit_events(doc, method=None):
	if doc.purpose == "Manufacture":
		update_item_code_in_batch(doc)

def update_item_code_in_batch(doc):
	for row in doc.items:
		if not row.batch_no: continue

		batch_item_code = frappe.get_cached_value("Batch", row.batch_no, "item")
		if ((row.is_finished_item or row.is_scrap_item) and row.batch_no
			and batch_item_code != row.item_code):

			make_batch(frappe._dict({
				"item": batch_item_code,
				"qty_to_produce": row.qty,
				"reference_doctype": "Work Order",
				"reference_name": doc.work_order
			}))

			frappe.db.set_value("Batch", row.batch_no, {
				"item": row.item_code,
				"item_name": row.item_name,
				"stock_uom": row.stock_uom
			})

def before_validate_events(doc, method=None):
	if doc.purpose == "Manufacture":
		update_fg_completed_qty(doc)

def update_fg_completed_qty(doc):
	fg_completed_qty = 0.0
	for row in doc.items:
		if row.is_finished_item:
			fg_completed_qty += row.qty

	doc.fg_completed_qty = fg_completed_qty
