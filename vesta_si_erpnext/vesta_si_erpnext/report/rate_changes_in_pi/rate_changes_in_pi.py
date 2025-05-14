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
	group_by_clause = ''
	select_fields = ''
	order_by = 'ORDER BY pi.posting_date DESC'

	# Apply conditions based on filters
	if filters.get("from_date"):
		cond += f" AND pi.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		cond += f" AND pi.posting_date <= '{filters.get('to_date')}'"
	if filters.get("item_code"):
		cond += f" AND pii.item_code = '{filters.get('item_code')}'"
	if filters.get("purchase_invoice"):
		cond += f" AND pi.name = '{filters.get('purchase_invoice')}'"
	if filters.get("supplier"):
		cond += f" AND pi.supplier = '{filters.get('supplier')}'"

	# Decide Group By and Select clause
	if filters.get("group_by") == "Item Code":
		group_by_clause = "GROUP BY pii.item_code"
		select_fields = """
			pi.name as purchase_invoice,
			SUM(pri.base_rate) as old_rate,
			SUM(pii.base_rate) as new_rate,
			SUM((pii.base_rate - pri.base_rate)) as difference,
			ROUND((SUM(pii.base_rate - pri.base_rate) * 100 / SUM(pii.base_rate)), 2) as percentage,
			pii.item_code,
			pii.item_name,
			pi.supplier,
			user.full_name as user
		"""
	elif filters.get("group_by") == "Supplier":
		group_by_clause = "GROUP BY pi.supplier"
		select_fields = """
			pi.name as purchase_invoice,
			SUM(pri.base_rate) as old_rate,
			SUM(pii.base_rate) as new_rate,
			SUM((pii.base_rate - pri.base_rate)) as difference,
			ROUND((SUM(pii.base_rate - pri.base_rate) * 100 / SUM(pii.base_rate)), 2) as percentage,
			NULL as item_code,
			NULL as item_name,
			pi.supplier,
			user.full_name as user
		"""
	elif filters.get("group_by") == "Purchase Invoice":
		group_by_clause = "GROUP BY pi.name"
		select_fields = """
			pi.name as purchase_invoice,
			SUM(pri.base_rate) as old_rate,
			SUM(pii.base_rate) as new_rate,
			SUM((pii.base_rate - pri.base_rate)) as difference,
			ROUND((SUM(pii.base_rate - pri.base_rate) * 100 / SUM(pii.base_rate)), 2) as percentage,
			NULL as item_code,
			NULL as item_name,
			pi.supplier,
			user.full_name as user
		"""
	else:
		# No filter selected, show raw data (no group by, no aggregation)
		select_fields = """
			pi.name as purchase_invoice,
			pri.base_rate as old_rate,
			pii.base_rate as new_rate,
			(pii.base_rate - pri.base_rate) as difference,
			ROUND(((pii.base_rate - pri.base_rate) * 100 / pii.base_rate), 2) as percentage,
			pii.item_code,
			pii.item_name,
			pi.supplier,
			user.full_name as user,
			pi.posting_date
		"""
		group_by_clause = ''

	query = f"""
		SELECT {select_fields}
		FROM `tabPurchase Invoice Item` as pii 
		RIGHT JOIN `tabPurchase Receipt Item` as pri ON pri.name = pii.pr_detail
		LEFT JOIN `tabPurchase Invoice` as pi ON pi.name = pii.parent
		LEFT JOIN `tabUser` as user ON user.name = pi.modified_by
		WHERE pii.docstatus = 1 AND (pii.base_rate - pri.base_rate) != 0
		{cond}
		{group_by_clause}
		{order_by}
	"""

	data = frappe.db.sql(query, as_dict=True)
	return data
