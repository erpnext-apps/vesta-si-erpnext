# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from collections import defaultdict
import copy

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters):
	qi_wise_data = defaultdict(list)
	data = []
	conditions = ""

	if filters.get('rejected_item'):
		conditions += " and qis.analysis_item_code = '{item}'".format(item=filters.get('rejected_item'))

	if filters.get('batch_no'):
		conditions += " and qi.batch_no = '{batch}'".format(batch=filters.get('batch_no'))

	if filters.get('customer'):
		conditions += " and qi.customer = '{customer}'".format(customer=filters.get('customer'))

	result = frappe.db.sql("""
		select
			qi.name as quality_inspection,
			qi.item_code, qi.batch_no,
			qis.analysis_item_code as rejected_item,
			qis.rejected_parameters as rejected_params,
			qi.customer
		from
			`tabQuality Inspection` qi,
			`tabInspection Summary` qis
		where
			qis.parent = qi.name
			and qis.status = 'Rejected'
			and qi.docstatus = 1
			and qi.report_date between '{from_date}' and '{to_date}'
			{conditions}
		order by report_date
		""".format(
				conditions=conditions,
				from_date=filters.get('from_date'),
				to_date=filters.get('to_date')
			),
		as_dict=1, debug=1)

	for row in result:
		row_copy = copy.deepcopy(row)

		if not row.get("quality_inspection") in qi_wise_data:
			qi_wise_data[row.get("quality_inspection")] = []
		else:
			row_copy.quality_inspection = ""
			row_copy.item_code = ""

		qi_wise_data[row.get("quality_inspection")].append(row_copy)

	for group in qi_wise_data:
		for row in qi_wise_data[group]:
			data.append(row)

	return data

def get_columns():
	return [
		{
			"label":_("Quality Inspection"),
			"fieldname": "quality_inspection",
			"fieldtype": "Link",
			"options": "Quality Inspection",
			"width": 200
		},
		{
			"label":_("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"label":_("Batch No"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 120
		},
		{
			"label":_("Rejected Item"),
			"fieldname": "rejected_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"label":_("Rejected Parameters"),
			"fieldname": "rejected_params",
			"fieldtype": "Data",
			"width": 400
		},
		{
			"label":_("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		}
	]