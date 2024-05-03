# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_data(filters):
	cond = ''
	if filters.get('company'):
		cond += f" and company = '{filters.get('company')}'"
	if filters.get('from_date'):
		cond += f" and posting_date >= '{filters.get('from_date')}'"
	if filters.get('from_date'):
		cond += f" and posting_date <= '{filters.get('to_date')}'"
	data = frappe.db.sql(f"""
					Select name, 
					posting_date, 
					workflow_state, 
					material_shipped_on, 
					base_net_total, 
					base_grand_total,
					total_qty,
					customer
					From `tabSales Invoice` 
					Where docstatus = 1 {cond}
	""",as_dict = 1)
	return data

def get_columns(filters):
	columns = [
		{
			"fieldname":'name',
			"label":"Sales Invoice",
			"fieldtype":'Link',
			"options":"Sales Invoice",
			"width":150
		},
		{
			"fieldname":'customer',
			"label":"Customer",
			"fieldtype":'Link',
			"options":"Customer",
			"width":150
		},
		{
			"fieldname":'posting_date',
			"label":"Posting Date",
			"fieldtype":'Date',
			"width":150
		},
		{
			"fieldname":'material_shipped_on',
			"label":"Material Shipped On",
			"fieldtype":'Date',
			"width":150
		},
		{
			"fieldname":'base_net_total',
			"label":"Net Total",
			"fieldtype":'Currency',
			"width":150
		},
		{
			"fieldname":'base_grand_total',
			"label":"Grand Total",
			"fieldtype":'Currency',
			"width":150
		},
		{
			"fieldname":'total_qty',
			"label":"Total Quantity",
			"fieldtype":'Float',
			"width":150
		},
	]
	return columns
