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
			"fieldname" : "old_value",
			"label" : "Old Value",
			"fieldtype" : "Currency",
			"width" : 200
		},
		{
			"fieldname" : "currenct_value",
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

	version = frappe.db.sql(f"""
				SELECT 
					vr.name, 
					vr.data, 
					vr.docname,
					pi.name as purchase_invoice, pi.owner, 
					pi.supplier,
					pi.posting_date,
					vr.owner
				FROM 
					`tabVersion` AS vr
				LEFT JOIN 
					`tabPurchase Invoice` AS pi 
				ON 
					vr.docname = pi.name
				WHERE 
					pi.docstatus = 1 
					AND vr.ref_doctype = 'Purchase Invoice' {cond}
			""", as_dict=1)

	purchase_invoice = frappe.db.sql(f"""
			SELECT 
				pi.name,
				pii.item_code,
				pii.item_name,
				pii.idx
			From `tabPurchase Invoice` as pi
			Left Join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
			Where pi.docstatus = 1 {cond}
	""", as_dict=1)
	pi_map = {}
	for row in purchase_invoice:
		if pi_map.get(row.name):
			pi_map[row.name].append(row)
		else:
			pi_map[row.name] = [row]
	value = []
	for row in version:
		if "row_changed" in row.data and "base_rate" in row.data:
			data = json.loads(row.data)
			if data.get("row_changed"):
				if data.get("row_changed")[0][0] == "items":
					for d in data.get("row_changed")[0][-1]:
						if d[0] == "base_rate":
							print(d)
							old_value = d[-2].replace("SEK", "").replace(",",".").replace(" " ,"") if not d[-2] == 0.0 else 0
							currenct_value =d[-1].replace("SEK", "").replace(",",".").replace(" " ,"") if not d[-1] == 0.0 else 0
							value.append({
								"purchase_invoice" : row.get("purchase_invoice"),
								"posting_date" : row.get("posting_date"),
								"user" : row.get("owner"),
								"supplier" : row.get("supplier"),
								"old_value" : flt(old_value),
								"currenct_value" : flt(currenct_value),
								"difference" : flt(old_value) - flt(currenct_value),
								"percentage" : round((flt(old_value) - flt(currenct_value)) * 100 / flt(old_value), 2) if old_value !=0 else 0,
								"idx" : data.get("row_changed")[0][1],
 							})
	for row in value:
		if pi_map.get(row.get("purchase_invoice")):
			for d in pi_map.get(row.get("purchase_invoice")):
				if (d.get("idx")) - 1 == row.get("idx"):
					row.update({
						"item_code" : d.get("item_code"),
						"item_name" : d.get("item_name")
					})
	return value