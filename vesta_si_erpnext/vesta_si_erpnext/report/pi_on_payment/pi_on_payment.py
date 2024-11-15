# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe import _


def execute(filters=None):
	columns, data = [], []
	data, columns, chart = get_data_from_pe(filters)
	return columns, data, None, chart


def get_data_from_pe(filters):
	cond = ''
	if filters.get("from_date"):
		cond += f" and  pe.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		cond += f" and pe.posting_date <= '{filters.get('to_date')}'"
	
	data = frappe.db.sql(f"""
				Select pe.name as payment_entry,
				pe.posting_date,
				pe.docstatus,
				pe.status,
				per.reference_doctype, 
				per.reference_name,
				pi.due_date,
				pi.name as purchase_invoice	
				From `tabPayment Entry Reference` as per
				Left Join `tabPayment Entry` as pe ON pe.name = per.parent and per.reference_doctype = "Purchase Invoice"
				Left Join  `tabPurchase Invoice` as pi ON pi.name = per.reference_name
				Where pe.docstatus != 2 and per.reference_doctype = "Purchase Invoice" {cond}
	""", as_dict =1)

	month_wise_data = {}
	month_wise_data, month_year = get_month_year_list(filters.get("from_date"), filters.get("to_date"), month_wise_data)
	on_time_row = []
	delay_payment_row = []
	for row in data:
		delay = (row.posting_date - row.due_date).days
		row.update({"delay" : delay})
		if filters.get("chart_type") == "Payment On Time":
			if flt(delay) <= 0:
				month_wise_data.update({getdate(row.posting_date).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.posting_date).strftime("%B_%Y"))) + 1})
				on_time_row.append(row)
		if filters.get("chart_type") == "Payments On Delay":
			if flt(row.delay) > 0:
				month_wise_data.update({getdate(row.posting_date).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.posting_date).strftime("%B_%Y"))) + 1})
				delay_payment_row.append(row)
	value = []
	for row in month_year:
		value.append(month_wise_data.get(row))


	chart = prepare_chart(month_year, value, filters)
	columns  = [
		{
			"label" : "Purchase Invoice",
			"fieldname" : "purchase_invoice",
			"fieldtype" : "Link",
			"options" : "Purchase Invoice",
			"width" : 170
		},
		{
			"label" : "Payment Entry",
			"fieldname" : "payment_entry",
			"fieldtype" : "Link",
			"options" : "Payment Entry",
			"width" : 170
		},
		{
			"label" : "PE Status",
			"fieldname" : "status",
			"fieldtype" : "Data",
			"width" : 150
		},
		{
			"label" : "PE Posting Date",
			"fieldname" : "posting_date",
			"fieldtype" : "Date",
			"width" : 150
		},
		{
			"label" : "Due date",
			"fieldname" : "due_date",
			"fieldtype" : "Date",
			"width" : 150
		},
		{
			"label" : "Delay",
			"fieldname" : "delay",
			"fieldtype" : "Data",
			"width" : 150
		}

	]
	if filters.get("chart_type") == "Payment On Time":
		return on_time_row, columns , chart

	if filters.get("chart_type") == "Payments On Delay":
		return delay_payment_row, columns, chart

from datetime import datetime, timedelta

def get_month_year_list(start_date_str, end_date_str, month_wise_data):

	start_date = getdate(start_date_str) 
	end_date = getdate(end_date_str)
	month = []
	
	current_date = start_date
	while current_date <= end_date:
		month_year = current_date.strftime("%B_%Y")
		month_wise_data.update({month_year : 0})
		month.append(month_year)
		next_month = current_date.replace(day=28) + timedelta(days=4)
		current_date = next_month.replace(day=1)
	
	return month_wise_data, month	

def prepare_chart(month_year, value, filters):
	
	chart = {
		"data": {
			"labels": month_year,
			"datasets": [
				{
					"name": _("Number of Payment On Time" if filters.get("chart_type") == "Payment On Time" else "Number of delay Payments"),
					"chartType": "bar",
					"values": value,
					'colors': ['#743ee2' if filters.get("chart_type") == "Payment On Time" else '#F683AE' ],
				}
			],
		},
		"type": "bar",
		"height": 500,
		'colors': ['#743ee2' if filters.get("chart_type") == "Payment On Time" else '#F683AE'],
	}
	return chart