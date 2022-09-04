# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json



def execute(filters=None):
	if not filters:
		filters = frappe._dict({})

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	accounting_standard = filters.get("accounting_standard")

	conditions = " and pi.docstatus = 1 "
	if accounting_standard:
		conditions += f" and pii.accounting_standard = {frappe.db.escape(accounting_standard)} "


	columns = [
		{
			"label": _("Item Tax Template"),
			"fieldname": "item_tax_template",
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"width": 120,
		},
		{
			"label": _("Sum of Net Total"),
			"fieldname": "gross_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	]

	tax_template_for_columns = {}
	data = []

	docs = frappe.db.sql(f""" select pii.item_tax_rate, pii.item_tax_template, pii.base_net_amount from `tabPurchase Invoice Item` as pii
	inner join `tabPurchase Invoice` as pi on pi.name = pii.parent and pi.posting_date between %(from_date)s
	and %(to_date)s {conditions}""",
	{"from_date": from_date, "to_date": to_date}, as_dict = 1)


	if not docs:
		return [], []

	for doc in docs:
		tax_heads = json.loads(doc.item_tax_rate)
		tax_total = 0
		for key in tax_heads:
			tax_total += tax_heads[key]

		if doc.item_tax_template in tax_template_for_columns:
			tax_template_for_columns[doc.item_tax_template]["tax_total"] += tax_total
			tax_template_for_columns[doc.item_tax_template]["item_net_amount"] += doc.base_net_amount
			for key in tax_heads:
				if key in tax_template_for_columns[doc.item_tax_template]:
					tax_template_for_columns[doc.item_tax_template][key] += tax_heads[key]
				else:
					tax_template_for_columns[doc.item_tax_template][key] = tax_heads[key]
		else:
			tax_template_for_columns[doc.item_tax_template] = {"tax_total": tax_total, "item_net_amount": doc.base_net_amount}
			tax_template_for_columns[doc.item_tax_template].update(tax_heads)

	column_account_heads = []
	for key in tax_template_for_columns:
		row = {
			"item_tax_template": key,
			"tax_total": tax_template_for_columns[key]["tax_total"],
			"gross_total": tax_template_for_columns[key]["item_net_amount"]
		}
		for head in tax_template_for_columns[key]:
			if head == 'tax_total' or head == 'item_net_amount':
				continue
			if not head in column_account_heads:
				column_account_heads.append(head)
				columns.append(
					{
						"label": head,
						"fieldname": head,
						"fieldtype": "Currency",
						"options": "currency",
						"width": 120,
						"default": 0
					}
				)
			row[head] = tax_template_for_columns[key][head]

		data.append(row)
	columns.append(
		{
			"label": _("Sum of Tax Total"),
			"fieldname": "tax_total",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	)
	return columns, data