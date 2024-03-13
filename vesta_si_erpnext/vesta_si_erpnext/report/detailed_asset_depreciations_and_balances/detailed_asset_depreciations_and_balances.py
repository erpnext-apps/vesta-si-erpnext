# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = [
		{
			"label": _("Asset"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Asset",
			"width": 120,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Gross Purchae Amount"),
			"fieldname": "gross_purchase_amount",
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"label": _("Accumulated Depreciation"),
			"fieldname": "accumulated_depreciation",
			"fieldtype": "Currency",
			"width": 270,
		},
	]
	data = get_asset_details(filters)
	return columns, data


def get_asset_details(filters):
	condition = ''
	if filters.get('asset_category'):
		condition += f" and asset_category = '{filters.get('asset_category')}'"
	if filters.get('to_date'):
		condition += f" and purchase_date <= '{filters.get('to_date')}'"
	data = frappe.db.sql(f""" 
		Select name, item_code, item_name, gross_purchase_amount, opening_accumulated_depreciation , asset_category
		From `tabAsset`
		where docstatus = 1  {condition}
	 """,as_dict = 1)
	condition = ''
	if filters.get('to_date'):
		condition += f" and posting_date <= '{filters.get('to_date')}'"
	for row in data:
		gle_data = frappe.db.sql(f"""
			Select sum(debit) as debit
			From `tabGL Entry`
			Where against_voucher = '{row.name}' and is_cancelled = 0 {condition}
			Group By against_voucher 
		""",as_dict = 1)
		if gle_data:
			row.update({'accumulated_depreciation': row.opening_accumulated_depreciation + gle_data[0].get('debit') })
		else:
			row.update({'accumulated_depreciation': row.opening_accumulated_depreciation})

	return data

	