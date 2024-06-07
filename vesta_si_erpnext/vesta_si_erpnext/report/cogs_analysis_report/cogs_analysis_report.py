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
		cond += f" and gl.posting_date >= '{filters.get('from_date')}'"
	if filters.get('to_date'):
		cond += f" and gl.posting_date <= '{filters.get('to_date')}'"
	if filters.get('customer_group') == "SKF":
		cond += f" and cu.customer_group = 'SKF Customer'"
	if filters.get('customer_group') == 'Non-SKF':
		cond += f" and cu.customer_group != 'SKF Customer'"

	data = frappe.db.sql(f"""
		Select gl.name as gl_entry,
		gl.posting_date,
		gl.voucher_no as name,
		CASE 
			WHEN gl.debit != 0 THEN gl.debit 
			ELSE -gl.credit 
		END AS base_net_amount,
		si.name, 
		cu.customer_name,
		si.customer,
		cu.customer_group
		From `tabGL Entry` as gl
		right Join `tabAccount` as acc ON acc.name = gl.account and acc.account_type = 'Cost of Goods Sold'
		Left Join `tabSales Invoice` as si ON si.name = gl.voucher_no
		Left Join `tabCustomer` as cu ON cu.name = si.customer
		where gl.is_cancelled = 0 and gl.is_opening = 'No' and gl.voucher_type = "Sales Invoice" {cond}
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