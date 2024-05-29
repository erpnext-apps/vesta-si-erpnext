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
	if filters.get('from_date'):
		cond += f" and si.posting_date >= '{filters.get('from_date')}'"
	if filters.get('to_date'):
		cond += f" and si.posting_date <= '{filters.get('to_date')}'"
	if filters.get('customer_group') == "SKF":
		cond += f" and si.customer_group = 'SKF Customer'"
	if filters.get('customer_group') == 'Non-SKF':
		cond += f" and si.customer_group != 'SKF Customer'"

	data = frappe.db.sql(f"""
		Select 
		si.name,
		si.posting_date,
		si.customer,
		si.customer_name,
		sum(sii.base_net_amount) as base_net_amount,
		cu.customer_group
		From `tabSales Invoice` as si
		Left Join `tabSales Invoice Item` as sii ON sii.parent = si.name
		left join `tabCustomer` as cu ON si.customer=cu.name
		Where si.docstatus = 1 {cond}
		Group By si.name
	""",as_dict = 1)
	for row in data:
		if row.customer_group == "SKF Customer":
			row.update({"customer_group":"SKF" })
		else:
			row.update({"customer_group":"Non-SKF" })
	return data

def get_columns(filters):
	return [
		{
			"fieldname":"name",
			"label":"Invoice ID",
			"fieldtype":"Link",
			"options":"Sales Invoice"
		},
		{
			"fieldname":"posting_date",
			"label":"Invoice Date",
			"fieldtype":"Date",
		},
		{
			"fieldname":"customer",
			"label":"Customer ID",
			"fieldtype":"Link",
			"options":"Customer"
		},
		{
			"fieldname":"customer_name",
			"label":"Customer Name",
			"fieldtype":"Data"
		},
		{
			"fieldname":"base_net_amount",
			"label":"COGS Amount",
			"fieldtype":"Float"
		},
		{
			"fieldname":"customer_group",
			"label":"Customer Group",
			"fieldtype":"Data"
		},

	]