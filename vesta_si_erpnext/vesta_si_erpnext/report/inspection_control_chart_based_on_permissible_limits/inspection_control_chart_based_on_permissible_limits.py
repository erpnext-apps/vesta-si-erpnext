# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns(filters)
	chart = prepare_chart(data)
	return columns, data, None, chart

def get_data(filters):
	condition = ''
	if filters.get('item_code'):
		condition += f" and qi.item_code = '{filters.get('item_code')}'"
	if filters.get('from_date'):
		condition += f" and qi.report_date >= '{filters.get('from_date')}'"
	if filters.get('to_date'):
		condition += f" and qi.report_date <= '{filters.get('to_date')}'"
	if filters.get('qi_parameter'):
		condition += f" and qri.specification = '{filters.get('qi_parameter')}'"
	
	qi_data = frappe.db.sql(f"""Select qi.name, qi.item_code, qri.specification, qri.min_value, qri.max_value, qri.reading_1
								From `tabQuality Inspection` as qi
								Left Join `tabQuality Inspection Reading` as qri ON qri.parent = qi.name
								Where qi.docstatus = 1 and qri.numeric = 1 {condition}
							""",as_dict =1)
	
	return qi_data

def get_columns(filters):
	columns = [
		{
			"fieldname":"name",
			"label": _("Quality Inspection"),
			"fieldtype": "Link",
			"options": "Quality Inspection",
			"width":150
		},
		{
			"fieldname":"item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width":150
		},
		{
			"fieldname":"specification",
			"label": _("QI Parameter"),
			"fieldtype": "Link",
			"options": "Quality Inspection Parameter",
			"width":150
		},
		{
			"fieldname":"reading_1",
			"label": _("Reading"),
			"fieldtype": "Float",
			"width":150
		},
		{
			"fieldname":"max_value",
			"label": _("Maximum Value"),
			"fieldtype": "Float",
			"width":150
		},
		{
			"fieldname":"min_value",
			"label": _("Minimum Value"),
			"fieldtype": "Float",
			"width":150
		},
	]
	
	return columns

def prepare_chart(data):
	return {
			
			"data": {
					'labels': [row.name for row in data],
					'datasets': [
						{
							'name': 'Max Value',
							'values': [row.max_value for row in data],
							'chartType': 'line',
						},
						{
							'name': "Reading",
							'values': [row.reading_1 for row in data],
							'chartType': 'line',
						},
						{
							'name': "Min Value",
							'values': [row.min_value for row in data],
							'chartType': 'line',
						},
						
					]
				},
				"type": "line",
				"colors": ["#008000", "#0000FF", "#FF0000"],
			}