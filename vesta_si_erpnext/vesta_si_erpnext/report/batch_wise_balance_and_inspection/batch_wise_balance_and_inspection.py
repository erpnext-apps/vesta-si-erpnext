# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate


def execute(filters=None):
	if not filters: filters = {}
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters)
	print(columns)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision)

	data = []
	for item in sorted(iwb_map):
		if not filters.get("item") or filters.get("item") == item:
			for wh in sorted(iwb_map[item]):
				for batch in sorted(iwb_map[item][wh]):
					batch_details_dict = iwb_map[item][wh][batch]
					if batch_details_dict.bal_qty:
						data.append([item, item_map[item]["item_name"], wh, batch,
							flt(batch_details_dict.bal_qty, float_precision),
							item_map[item]["stock_uom"], batch_details_dict.qi, batch_details_dict.iron, batch_details_dict.calcium,
							batch_details_dict.aluminium, batch_details_dict.supplier_bag_no
						])

	return columns, data


def get_columns(filters):
	"""return columns based on filters"""

	columns = [_("Item") + ":Link/Item:100"] + [_("Item Name") + "::150"] + [_("Warehouse") + ":Link/Warehouse:100"] + \
		[_("Batch") + ":Link/Batch:100"] + [_("Balance Qty") + ":Float:90"] + [_("UOM") + "::90"] + \
		[_("Quality Inspection") + ":Link/Quality Inspection:140"] + [_("Iron Content") + ":Float:100"] + \
		[_("Calcium Content") + ":Float:100"] + [_("Aluminium Content") + ":Float:100"] + [_("Supplier Bag No.") + "::140"]

	return columns


def get_conditions(filters):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and posting_date <= '%s'" % filters["to_date"]
	else:
		frappe.throw(_("'To Date' is required"))

	for field in ["item_code", "warehouse", "batch_no", "company"]:
		if filters.get(field):
			conditions += " and {0} = {1}".format(field, frappe.db.escape(filters.get(field)))
	
	if filters.get("quality_inspection"):
		conditions += " and se.quality_inspection like {0}".format(frappe.db.escape(filters.get('quality_inspection')))

	if filters.get("iron_content"):
		iron_content = '%' + filters.get('iron_content') + '%'
		conditions += " and reading.iron like {0}".format(frappe.db.escape(iron_content, percent = False))

	if filters.get("calcium_content"):
		cal_content = '%' + filters.get('calcium_content') + '%'
		conditions += " and reading.calcium like {0}".format(frappe.db.escape(cal_content, percent = False))

	if filters.get("aluminium_content"):
		alum_content = '%' + filters.get('aluminium_content') + '%'
		conditions += " and reading.aluminium like {0}".format(frappe.db.escape(alum_content, percent = False))

	if filters.get("supplier_bag_no"):
		supplier_bag_no = '%' + filters.get('supplier_bag_no') + '%'
		conditions += " and se.supplier_bag_no like {0}".format(frappe.db.escape(supplier_bag_no), percent = False)

	return conditions


# get all details
def get_stock_ledger_entries(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
		select s.item_code, s.batch_no, s.warehouse, s.posting_date, sum(s.actual_qty) as actual_qty,
			se.quality_inspection as qi_name, reading.iron as iron, reading.calcium as cal, reading.aluminium as alum,
			se.supplier_bag_no as supplier_bag_no
		from `tabStock Ledger Entry` s
		left join `tabStock Entry Detail` se on s.voucher_no = se.parent and se.batch_no= s.batch_no
		left join (
			select parent 
				,MAX(case when specification = 'Iron Content' then reading_1 end) iron
				,MAX(case when specification = 'Calcium Content' then reading_1 end) calcium
				,MAX(case when specification = 'Aluminium Content' then reading_1 end) aluminium 
			from `tabQuality Inspection Reading` group by parent) as reading	
		on se.quality_inspection = reading.parent
		where s.is_cancelled = 0 and s.docstatus < 2 and ifnull(s.batch_no, '') != '' %s
		group by voucher_no, batch_no, item_code, warehouse
		order by item_code, warehouse""" %
		conditions, as_dict=1, debug = True)
	
def get_item_warehouse_batch_map(filters, float_precision):
	sle = get_stock_ledger_entries(filters)
	iwb_map = {}

	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])

	for d in sle:
		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {})\
			.setdefault(d.batch_no, frappe._dict({
				"opening_qty": 0.0,
				"in_qty": 0.0,
				"out_qty": 0.0,
				"bal_qty": 0.0,
				"qi": "",
				"iron": "",
				"calcium": "",
				"aluminium": "",
				"supplier_bag_no": ""
			}))
		batch_details_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
		batch_details_dict.qi = d.qi_name
		batch_details_dict.iron = flt(d.iron)
		batch_details_dict.calcium = flt(d.cal)
		batch_details_dict.aluminium = flt(d.alum)
		batch_details_dict.supplier_bag_no = d.supplier_bag_no
		batch_details_dict.bal_qty = flt(batch_details_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)

	return iwb_map


def get_item_details(filters):
	item_map = {}
	for d in frappe.db.sql("select name, item_name, description, stock_uom from tabItem", as_dict=1):
		item_map.setdefault(d.name, d)

	return item_map
