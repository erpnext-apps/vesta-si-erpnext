# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
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
		if doc.is_new():
			set_indicators(doc)

def update_fg_completed_qty(doc):
	fg_completed_qty = 0.0
	for row in doc.items:
		if row.is_finished_item:
			fg_completed_qty += row.qty

	doc.fg_completed_qty = fg_completed_qty

def set_indicators(doc):
	"""Set 'Analysis Required' on rows as a helper for js color indicators."""
	start_idx, fg_analysis_frequency, fg_item = None, None, None
	last_idx = doc.items[-1].idx

	# get finished item first row
	start_idx = [row.idx for row in doc.items if row.is_finished_item][0]
	fg_item = doc.items[start_idx - 1].item_code
	fg_analysis_frequency = frappe.db.get_value("Item", fg_item, "analysis_frequency")

	if not start_idx or not fg_analysis_frequency: return

	inspect_idx = start_idx # start marking from start_idx
	while inspect_idx <= last_idx:
		if doc.items[inspect_idx - 1].item_code == fg_item:
			doc.items[inspect_idx - 1].analysis_required = 1
			inspect_idx += fg_analysis_frequency

def set_quality_inspection(doc,  method=None):
	for item in doc.items:
		if item.outpacking_rm and not item.t_warehouse and item.is_finished_item:   # there will be only one drum(raw material) in an out-packing work order scenario
			qi = frappe.get_all("Quality Inspection", filters={'batch_no': item.batch_no}, order_by = 'creation desc')
			if qi:
				for fg_item in doc.items:
					if fg_item.t_warehouse and fg_item.is_finished_item:
						fg_item.rm_quality_inspection = qi[0].name

def validate_outpacking_raw_material(doc, method=None):
	is_outpacking_wo = frappe.db.get_value("Work Order", doc.work_order, "is_outpacking_wo")
	if is_outpacking_wo:
		rm = 0
		for item in doc.items:
			if item.outpacking_rm:
				rm += 1
		if rm != 1:
			frappe.throw(_("There can't be multiple drums as raw material in the items table"))
