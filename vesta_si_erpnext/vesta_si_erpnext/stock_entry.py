# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from vesta_si_erpnext.vesta_si_erpnext.quality_inspection import get_template_details_with_frequency
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
		set_indicators(doc)

	from vesta_si_erpnext.vesta_si_erpnext.putaway_rule import apply_putaway_rule

	doc.custom_apply_putaway_rule = 0
	if doc.apply_putaway_rule:
		doc.apply_putaway_rule = 0

		apply_putaway_rule(doc.doctype, doc.get("items"), doc.company)

		doc.custom_apply_putaway_rule = 1

def update_fg_completed_qty(doc):
	fg_completed_qty = 0.0
	for row in doc.items:
		if row.is_finished_item:
			fg_completed_qty += row.qty

	doc.fg_completed_qty = fg_completed_qty

# to reduce the number of frequencies while marking the indicators
def check_if_divisible(drum_no, freqs):
	for freq in freqs:
		if freq == 0:
			freq = 1

		if drum_no % freq == 0:
			return True

def set_indicators(doc):
	"""Set 'Analysis Required' on rows as a helper for js color indicators."""
	start_idx, fg_item = None, None
	last_idx = doc.items[-1].idx

	# get finished item first row
	start_idx = [row.idx for row in doc.items if row.is_finished_item][0]
	fg_item = doc.items[start_idx - 1].item_code

	template = frappe.db.get_value('Item', fg_item, 'quality_inspection_template')
	template_readings = get_template_details_with_frequency(template)
	freqs = set([reading.frequency for reading in template_readings])
	if not start_idx : return

	inspect_idx = start_idx # start marking from start_idx

	while inspect_idx <= last_idx:
		drum_no = inspect_idx - (start_idx)

		# mark all drumns that match the freq in the template
		if (doc.items[inspect_idx - 1].item_code == fg_item and
			(inspect_idx == start_idx or check_if_divisible(drum_no, freqs))):
			doc.items[inspect_idx - 1].analysis_required = 1
		else:
			doc.items[inspect_idx - 1].analysis_required = 0

		inspect_idx += 1

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
