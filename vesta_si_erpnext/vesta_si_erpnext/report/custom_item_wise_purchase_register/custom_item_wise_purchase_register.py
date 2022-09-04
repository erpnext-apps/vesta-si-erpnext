# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from erpnext.accounts.report.item_wise_purchase_register.item_wise_purchase_register import execute as parent_report



def execute(filters=None):
	columns, data, message, chart, report_summary, skip_total_row = parent_report(filters)

	# Did not do any optimizations here considering the upgrades. Achieving this by means of simple itertions.
	final_columns = []
	for column in columns:
		final_columns.append(column)
		if column["fieldname"] == "item_name":
			final_columns.append({
				"label": _("Item Tax Template"),
				"fieldname": "item_tax_template",
				"fieldtype": "Link",
				"options": "Item Tax Template",
				"width": 120,
			})
	final_data = []
	for datum in data:
		if datum["item_code"] and datum["invoice"]:
			datum["item_tax_template"] = frappe.db.get_value("Purchase Invoice Item",
			{"parent": datum["invoice"], "item_code": datum["item_code"]},
			"item_tax_template")
		final_data.append(datum)

	return final_columns, final_data, message, chart, report_summary, skip_total_row
