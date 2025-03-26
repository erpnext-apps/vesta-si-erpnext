# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import flt

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = [
		{
			"fieldname" : "purchase_invoice",
			"label" : "Purchase Invoice",
			"options" : "Purchase Invoice",
			"fieldtype" : "Link",
			"width" : 200
		},
		{
			"fieldname" : "posting_date",
			"label" : "Date",
			"fieldtype" : "Date",
			"width" : 200
		},
		{
			"fieldname" : "supplier",
			"label" : "Supplier",
			"options" : "Supplier",
			"fieldtype" : "Link",
			"width" : 200
		},
		{
			"fieldname" : "item_code",
			"label" : "Item Code",
			"options" : "Item",
			"fieldtype" : "Link",
			"width" : 200
		},
		{
			"fieldname" : "item_name",
			"label" : "Item Name",
			"fieldtype" : "Data",
			"width" : 200
		},
		{
			"fieldname" : "old_rate",
			"label" : "Old Value",
			"fieldtype" : "Currency",
			"width" : 200
		},
		{
			"fieldname" : "new_rate",
			"label" : "Current Value",
			"fieldtype" : "Currency",
			"width" : 200
		},
		{
			"fieldname" : "difference",
			"label" : "Difference",
			"fieldtype" : "Currency",
			"width" : 200
		},
		{
			"fieldname" : "percentage",
			"label" : "Percentage",
			"fieldtype" : "Percentage",
			"width" : 200
		},
		{
			"fieldname" : "user",
			"label" : "User",
			"fieldtype" : "Link",
			"options" : "User",
			"width" : 200
		}
	]
	return columns, data


def get_data(filters):
	cond = ''
	if filters.get("from_date"):
		cond += f" AND pi.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		cond += f" AND pi.posting_date <= '{filters.get('to_date')}'"
	if filters.get("item_code"):
		cond += f" AND pii.item_code = '{filters.get('item_code')}'"

	data = frappe.db.sql(f"""
			Select pi.name as purchase_invoice,
			pri.base_rate as old_rate,
			pii.base_rate as new_rate,
			(pii.base_rate - pri.base_rate) as difference,
			ROUND(((pri.base_rate - pii.base_rate) * 100 / pii.base_rate), 2) as percentage,
			pii.item_code,
			pii.item_name,
			pi.supplier,
			user.full_name as user,
			pi.posting_date
			From `tabPurchase Invoice Item` as pii 
			Right Join `tabPurchase Receipt Item` as pri ON pri.name = pii.pr_detail
			Left Join `tabPurchase Invoice` as pi ON pi.name = pii.parent
			Left Join `tabUser` as user ON user.name = pi.modified_by
			Where pii.docstatus = 1 and (pii.base_rate - pri.base_rate) != 0 {cond}
	""", as_dict=1 )


	return data