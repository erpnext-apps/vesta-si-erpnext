# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe import _

def execute(filters=None):
	columns, data = [], []

	columns, data, chart = get_data(filters)

	return columns, data, None, chart

def get_data(filters):

	cond = ''
	if filters.get("from_date"):
		cond += f" and  pel.file_creation_time >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		cond += f" and pel.file_creation_time <= '{filters.get('to_date')}'"
	if filters.get("payment_export_log"):
		cond += f" and pel.name = '{filters.get('payment_export_log')}'"
	if filters.get("delay_payment"):
		cond += f" and ptl.delay > 0"

	data = frappe.db.sql(f"""
			Select pel.name, 
			pel.file_creation_time, 
			pel.currency, 
			ptl.payment_entry,
			ptl.document_type,
			ptl.purchase_doc_no,
			ptl.due_date,
			ptl.delay
			From `tabPayment Export Log` as pel
			Left Join `tabPayment Transaction Log` as ptl ON ptl.parent = pel.name
			where 1 = 1 and ptl.status != "Cancelled" {cond}
			Order By pel.file_creation_time DESC
	""", as_dict=1)

	removed = []
	month_wise_data = {}
	month_wise_data, month_year = get_month_year_list(filters.get("from_date"), filters.get("to_date"), month_wise_data)

	for row in data:
		if not filters.get("delay_payment"):
			if flt(row.delay) <= 0:
				month_wise_data.update({getdate(row.file_creation_time).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.file_creation_time).strftime("%B_%Y"))) + 1})
		else:
			month_wise_data.update({getdate(row.file_creation_time).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.file_creation_time).strftime("%B_%Y"))) + 1})
		
		if row.name not in removed:
			day = get_day(str(getdate(row.file_creation_time)))
			removed.append(row.name)
			row.update({"day" : day})
		else:
			row.update({"name" : ""})
	value = []
	
	for row in month_year:
		value.append(month_wise_data.get(row))

	columns  = [
		{
			"label" : "PE Log",
			"fieldname" : "name",
			"fieldtype" : "Link",
			"options" : "Payment Export Log",
			"width" : 150
		},
		{
			"label" : "Purchase Invoice",
			"fieldname" : "purchase_doc_no",
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
			"label" : "Payment Date",
			"fieldname" : "file_creation_time",
			"fieldtype" : "Datetime",
			"width" : 150
		},
		{
			"label" : "Day",
			"fieldname" : "day",
			"fieldtype" : "Data",
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

	chart = prepare_chart(month_year, value, filters)

	return columns, data, chart

def get_day(date_string):
	import datetime

	date_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d')

	day_of_week = date_obj.strftime('%A')

	return day_of_week

def prepare_chart(month_year, value, filters):
	
	chart = {
		"data": {
			"labels": month_year,
			"datasets": [
				{
					"name": _("Number of delay Payments" if filters.get("delay_payment") else "Number of on time payments"),
					"chartType": "bar",
					"values": value,
				}
			],
		},
		"type": "bar",
		"height": 500
	}
	return chart


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