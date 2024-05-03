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
		cond += f" and si.company = '{filters.get('company')}'"
	if filters.get('from_date'):
		cond += f" and si.posting_date >= '{filters.get('from_date')}'"
	if filters.get('from_date'):
		cond += f" and si.posting_date <= '{filters.get('to_date')}'"
	if filters.get('status'):
		cond += f" and si.status = '{filters.get('status')}'"
	if filters.get('item_code'):
		cond += f" and sii.item_code = '{filters.get('item_code')}'"

	data = frappe.db.sql(f"""
					Select si.name, 
					si.posting_date, 
					si.workflow_state, 
					si.material_shipped_on, 
					si.base_net_total,
					si.workflow_state, 
					si.base_grand_total,
					sii.qty,
					sii.net_amount,
					sii.base_net_amount,
					sii.item_code,
					sii.item_name,
					si.customer_name,
					si.currency
					From `tabSales Invoice` as si 
					Left join `tabSales Invoice Item` as sii ON sii.parent = si.name
					Where si.docstatus != 2 {cond}
	""",as_dict = 1)
	return data

def get_columns(filters):
	columns = [
		{
			"fieldname":'workflow_state',
			"label":"Workflow State",
			"fieldtype":'Data',
			"options":"Workflow State",
			"width":150
		},
		{
			"fieldname":'name',
			"label":"Sales Invoice",
			"fieldtype":'Link',
			"options":"Sales Invoice",
			"width":150
		},
		{
			"fieldname":"item_code",
			"fieldtype":'Link',
			"label":"Item Code",
			"options":"Item",
			"width":150
		},
		{
			"fieldname":"item_name",
			"fieldtype":'Data',
			"label":"Item Name",
			"width":150,
		},
		{
			"fieldname":'customer_name',
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
			"fieldname":'base_net_amount',
			"label":"Net Amount(SEK)",
			"fieldtype":'Currency',
			"width":150
		},
		{
			"fieldname":'net_amount',
			"label":"Net Amount",
			"fieldtype":'Currency',
			"options":"currency",
			"width":150
		},
		{
			"fieldname":'qty',
			"label":"Quantity",
			"fieldtype":'Float',
			"width":150
		},
		{
			"fieldname":'currency',
			"label":"Currency",
			"fieldtype":'Link',
			"options":"Currency",
			"width":150
		}
	]
	return columns