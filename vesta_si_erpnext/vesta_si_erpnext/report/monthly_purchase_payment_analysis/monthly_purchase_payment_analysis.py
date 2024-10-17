# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
	columns, data = [], []
	columns, data = get_data(filters)
	return columns, data

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
			where 1 = 1 {cond}
			Order By pel.file_creation_time DESC
	""", as_dict=1)

	removed = []

	for row in data:
		if row.name not in removed:
			day = get_day(str(getdate(row.file_creation_time)))
			removed.append(row.name)
			row.update({"day" : day})
		else:
			row.update({"name" : ""})

	columns  = [
		{
			"label" : "PE Log",
			"fieldname" : "name",
			"fieldtype" : "Link",
			"options" : "Payment Export Log",
			"width" : 150
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

	return columns, data

def get_day(date_string):
	import datetime

	date_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d')

	day_of_week = date_obj.strftime('%A')

	return day_of_week