# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe import _


def execute(filters=None):
	if not filters.get("range1"):
		frappe.throw("Ageing 1 can not be Zero ot null")
	if not filters.get("range2"):
		frappe.throw("Ageing 2 can not be Zero ot null")
	if not filters.get("range3"):
		frappe.throw("Ageing 3 can not be Zero ot null")
	if not filters.get("range4"):
		frappe.throw("Ageing 4 can not be Zero ot null")
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

	range1 = 0
	range2 = 0
	range3 = 0
	range4 = 0
	range5 = 0
	on_time = 0

	if not filters.get("range1"):
		filters.update({ "range1" : 30 })
	if not filters.get("range2"):
		filters.update({ "range2" : 60 })
	if not filters.get("range3"):
		filters.update({ "range3" : 90 })
	if not filters.get("range4"):
		filters.update({ "range4" : 120 })


	for row in data:
		delay = (row.posting_date - row.due_date).days
		row.update({"delay" : delay})
		if flt(row.delay) <= 0:
			on_time += 1
		if 0 < row.delay <= flt(filters.get('range1')) :
			range1 += 1
		if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
			range2 += 1
		if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
			range3 += 1
		if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
			range4 += 1
		if flt(filters.get('range4')) < flt(row.delay):
			range5 += 1
		
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
	
	labels = ["On Time"]
	if filters.get("range1"):
		label1 = "{0} to {1}".format(0, filters.get("range1"))
		labels.append(label1)
	if filters.get("range2") and filters.get("range1"):
		label2 = "{0} to {1}".format(int(flt(filters.get("range1"))+1), filters.get("range2"))
		labels.append(label2)
	if filters.get("range3") and filters.get("range2"):
		label3 = "{0} to {1}".format(int(flt(filters.get("range2"))+1), filters.get("range3"))
		labels.append(label3)
	if filters.get("range4") and filters.get("range3"):
		label4 = "{0} to {1}".format(int(flt(filters.get("range3"))+1), filters.get("range4"))
		labels.append(label4)
	if filters.get("range4"):
		label5 = "Greater than {0}".format(filters.get("range4"))
		labels.append(label5)

	chart = prepare_chart(on_time, range1, range2, range3, range4, range5, labels)
	
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

def prepare_chart(on_time, range1, range2, range3, range4, range5, labels):
	
	
	charts = {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Delayed", "values": [on_time, range1, range2, range3, range4, range5]}],
		},
		"type": "percentage",
		"colors": ["#84D5BA", "#CB4B5F"],
	}
	return charts
