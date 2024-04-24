# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	data = get_data(filters) or []
	columns = get_columns()

	return columns, data


def get_data(report_filters):
	filters = get_report_filters(report_filters)
	fields = get_report_fields()

	purchase_receipt = frappe.db.sql(f"""
		Select pr.name , pri.item_code, pri.base_net_amount as amount, pri.base_net_rate as rate, pri.purchase_invoice
		From `tabPurchase Receipt` as pr
		Left Join `tabPurchase Receipt Item` as pri on pri.parent = pr.name
		Where pr.company = '{report_filters.get('company')}' and pr.docstatus = 1 """,as_dict = 1)

	purchase_invoice = frappe.get_all("Purchase Invoice", fields=fields, filters=filters)

	pr_map = {}
	for row in purchase_receipt:
		pr_map[row.purchase_invoice] = row
	
	for row in purchase_invoice:
		if row.purchase_receipt:
			doc = frappe.get_doc('Purchase Receipt', row.purchase_receipt)
			for d in doc.items:
				if d.item_code == row.item_code:
					row.update({'pr_rate':d.base_net_rate})
					row.update({'pr_amount':d.base_net_amount})
			continue
		if pr_map.get(row.name) and not row.purchase_receipt:
			if pr_map.get(row.name).get('item_code') == row.item_code:
				row.update({'purchase_receipt':pr_map.get(row.name).get('name')})
				row.update({'pr_rate':pr_map.get(row.name).get('rate')})
				row.update({'pr_amount':pr_map.get(row.name).get('amount')})
		
	for row in purchase_invoice:
		if row.pr_amount:
			row.update({'difference_amount' : row.base_net_amount - flt(row.pr_amount)})
		
		
		
	return purchase_invoice



def get_report_filters(report_filters):
	filters = [
		["Purchase Invoice", "company", "=", report_filters.get("company")],
		["Purchase Invoice", "posting_date", "<=", report_filters.get("posting_date")],
		["Purchase Invoice", "docstatus", "=", 1],
		["Purchase Invoice", "per_received", "<", 100],
		["Purchase Invoice", "update_stock", "=", 0],
		["Purchase Invoice Item", "expense_account", "=", "222501 - Goods & services received/Invoice received - non SKF - 9150"]
	]

	if report_filters.get("purchase_invoice"):
		filters.append(
			["Purchase Invoice", "per_received", "in", [report_filters.get("purchase_invoice")]]
		)

	return filters


def get_report_fields():
	fields = []
	for p_field in ["name", "supplier", "company", "posting_date", "currency"]:
		fields.append("`tabPurchase Invoice`.`{}`".format(p_field))

	for c_field in ["item_code", "item_name", "uom", "qty", "received_qty", "base_net_rate", "base_net_amount", 'purchase_receipt']:
		fields.append("`tabPurchase Invoice Item`.`{}`".format(c_field))

	return fields


def get_columns():
	return [
		{
			"label": _("Purchase Invoice"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 170,
		},
		{
			"label": _("Purchase Receipt"),
			"fieldname": "purchase_receipt",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 170,
		},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 120,
		},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 100},
		{"label": _("UOM"), "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 100},
		{"label": _("Invoiced Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
		{"label": _("Received Qty"), "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
		{"label": _("Rate"), "fieldname": "base_net_rate", "fieldtype": "Currency", "width": 100},
		{"label": _("PR Rate"), "fieldname": "pr_rate", "fieldtype": "Currency", "width": 100},
		{"label": _("Amount"), "fieldname": "base_net_amount", "fieldtype": "Currency", "width": 100},
		{"label": _("PR Amount"), "fieldname": "pr_amount", "fieldtype": "Currency", "width": 100},
		{"label": _("Different Amount"), "fieldname": "difference_amount", "fieldtype": "Currency", "width": 100},

	]
