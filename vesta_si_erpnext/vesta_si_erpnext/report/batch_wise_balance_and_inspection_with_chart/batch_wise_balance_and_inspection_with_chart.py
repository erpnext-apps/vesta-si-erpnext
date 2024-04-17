# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import json
import frappe
from frappe import _
from frappe.utils import cint, flt, getdate
from pypika.terms import JSON
import statistics



def execute(filters=None):
	param_columns = get_params(filters)

	if not filters: filters = {}
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

	float_precision = cint(frappe.db.get_default("float_precision")) or 3

	columns = get_columns(filters, param_columns)
	item_map = get_item_details(filters)
	iwb_map = get_item_warehouse_batch_map(filters, float_precision, param_columns)
	data = []
	total = 0
	std_dev = []
	batch_list = []
	for item in sorted(iwb_map):
		if not filters.get("item") or filters.get("item") == item:
			for wh in sorted(iwb_map[item]):
				for batch in sorted(iwb_map[item][wh]):
					batch_dict = iwb_map[item][wh][batch]
					if batch_dict.qi:
						row = [item, item_map[item]["item_name"], wh, batch,
							flt(batch_dict.bal_qty, float_precision),
							item_map[item]["stock_uom"], batch_dict.qi
						]
						for param in param_columns:
							row.append(flt(batch_dict[param['col_name']]))
							std_dev.append(flt(batch_dict[param['col_name']]))
						data.append(row)
	
	avarage = sum(std_dev) / flt(len(data))
	stdev = statistics.stdev(std_dev)
	UCL = flt(avarage) + flt(stdev)
	LCL = flt(avarage) - flt(stdev)
	for row in data:
		batch_list.append(row[3])
		row.extend([avarage, stdev, UCL, LCL])

	chart = get_chart_data(filters, columns, data, batch_list, avarage, stdev, UCL, LCL, std_dev)

	return columns, data , None, chart


def get_columns(filters, params):
	"""return columns based on filters"""

	columns = [_("Item") + ":Link/Item:100"] + [_("Item Name") + "::150"] + \
			[_("Warehouse") + ":Link/Warehouse:100"] + \
			[_("Batch") + ":Link/Batch:100"] + [_("Balance Qty") + ":Float:90"] + \
			[_("UOM") + "::90"] + \
			[_("Quality Inspection") + ":Link/Quality Inspection:140"]

	for param in params:
		columns += [_('QI Parameter') + ":Float:150"]
	columns += [_("Avarage") + ":Float:100"] + [_("Standard Deviation") + ":Float:100"] + \
				[_("UCL") + ":Float:100"] + [_("LCL") + ":Float:100"]
	return columns


def get_conditions(filters, params):
	conditions = ""
	if not filters.get("from_date"):
		frappe.throw(_("'From Date' is required"))

	if filters.get("to_date"):
		conditions += " and posting_date <= '%s'" % filters["to_date"]
	else:
		frappe.throw(_("'To Date' is required"))

	for field in ["item_code", "warehouse", "batch_no", "company"]:
		if filters.get(field):
			conditions += " and s.{0} = {1}".format(field, frappe.db.escape(filters.get(field)))

	for param in params:
		if filters.get(param['col_name']):
			parameter = '%' + filters.get(param['col_name']) + '%'
			conditions += " and reading." + param['col_name'] + " like {0}".format(frappe.db.escape(parameter, percent = False))

	
	return conditions


# get all details
def get_stock_ledger_entries(filters, params):
	conditions = get_conditions(filters, params)
	param_conditions = ""
	for param in params:
		param_conditions += ",MAX(case when specification = {0} then reading_1 end) as {1}" \
			.format(frappe.db.escape(param['inspection_parameter'], percent = False), param['col_name'])

	col_conditions = ""
	for col in params:
		col_conditions += ", reading." + col['col_name'] + " as " + col['col_name']

	conditions += f" and qi.report_date >= '{filters.get('from_date')}'"
	conditions += f" and qi.report_date <= '{filters.get('to_date')}'"
	
	data = frappe.db.sql(f"""
	 	SELECT
	 		s.item_code, s.batch_no, s.warehouse, s.posting_date, sum(s.actual_qty) as actual_qty,
	 		se.quality_inspection as qi_name {col_conditions}
	 	FROM
	 		(
			SELECT
				s.item_code, s.batch_no, s.warehouse, s.posting_date, sum(s.actual_qty) as actual_qty,
				s.voucher_no, s.is_cancelled, s.docstatus, s.company
			FROM
				`tabStock Ledger Entry` s
			GROUP BY
				s.batch_no, s.item_code, s.warehouse
				) as s
	 	LEFT JOIN
	 		`tabStock Entry Detail` se on s.voucher_no = se.parent and se.batch_no= s.batch_no
		LEFT JOIN (
	 		select parent {param_conditions} from `tabQuality Inspection Reading` GROUP BY parent
		) as reading on se.quality_inspection = reading.parent
	 	LEFT JOIN
	 		`tabQuality Inspection` qi on se.quality_inspection = qi.name
	 	WHERE
	 		s.is_cancelled = 0 and s.docstatus < 2 and ifnull(s.batch_no, '') != ''
	 		{conditions}
	 	GROUP BY
	 		batch_no, s.item_code, warehouse
	 	ORDER BY
	 		s.item_code, warehouse""", as_dict=1, debug=1)
	return data

def get_item_warehouse_batch_map(filters, float_precision, params):
	sle = get_stock_ledger_entries(filters, params)
	iwb_map = {}

	from_date = getdate(filters["from_date"])
	to_date = getdate(filters["to_date"])


	for d in sle:
		param_values = {}
		for param in params:
			param_values[param['col_name']] = ""
		iwb_map.setdefault(d.item_code, {}).setdefault(d.warehouse, {})\
			.setdefault(d.batch_no, frappe._dict({
				"opening_qty": 0.0,
				"in_qty": 0.0,
				"out_qty": 0.0,
				"bal_qty": 0.0,
				"qi": ""
			}))
		batch_dict = iwb_map[d.item_code][d.warehouse][d.batch_no]
		batch_dict.qi = d.qi_name
		batch_dict.supplier_bag_no = d.supplier_bag_no
		for param in param_values:
			batch_dict[param] = d[param]
		batch_dict.bal_qty = flt(batch_dict.bal_qty, float_precision) + flt(d.actual_qty, float_precision)
	return iwb_map

@frappe.whitelist()
def get_params(filters):
	import re
	params =  [{'inspection_parameter': filters.get('qi_parameter')}]

	for col in params:
		col['col_name'] = re.sub('[^A-Za-z0-9]+', '', str(col.get('inspection_parameter')))

	return params

def get_batch_desc(batch_no):
	desc = frappe.get_value('Batch', batch_no, 'description')
	return desc
def get_item_details(filters):
	item_map = {}
	for d in frappe.db.sql("select name, item_name, description, stock_uom from tabItem", as_dict=1):
		item_map.setdefault(d.name, d)

	return item_map


def get_chart_data(filters, columns, data, batch_list, avarage, stdev, UCL, LCL, std_dev):
	avarage_list = [avarage for row in range(len(data))]
	UCL = [UCL for row in range(len(data))]
	LCL = [LCL for row in range(len(data))]
	
	return {
			
			"data": {
					'labels': batch_list,
					'datasets': [
						{
							'name': 'Avarage',
							'values': avarage_list,
							'chartType': 'line'
						},
						{
							'name': "UCL",
							'values': UCL,
							'chartType': 'line'
						},
						{
							'name': "LCL",
							'values': LCL,
							'chartType': 'line'
						},
						{
							'name': "QI Parameter",
							'values': std_dev,
							'chartType': 'line'
						},
					]
				},
				"type": "line",
			}
