# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe import _

@frappe.whitelist()
def prepare_chart(filters =None):
    filters = json.loads(filters)
    if filters.get("fiscal_year"):
        doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
        year_start_date = doc.year_start_date
        year_end_date = doc.year_end_date
        filters.update({
            "from_date" : year_start_date,
            "to_date" : year_end_date
        })
    
    data = execute(filters)

    if filters.get("range1"):
        label1 = "{0} - {1}".format(0, filters.get("range1"))
    if filters.get("range2"):
        label2 = "{0} - {1}".format(filters.get("range1") + 1, filters.get("range1"))
    if filters.get("range3"):
        label3 = "{0} - {1}".format(filters.get("range2") + 1, filters.get("range3"))
    if filters.get("range3"):
        label4 = "{0} - {1}".format(filters.get("range2") + 1, filters.get("range3"))
    if filters.get("range4"):
        label4 = "{0} - {1}".format(filters.get("range3") + 1, filters.get("range4"))
    if filters.get("range4"):
        label5 = "{0} - {1}".format("Above", filters.get("range4"))

    labels = [
        "January" ,
        "February" ,
        "March" ,
        "April" ,
        "May" ,
        "June" ,
        "July" ,
        "August" , 
        "September" , 
        "October" ,
        "November" ,
        "December" 
    ]
    chart_data_map = {}
    for row in labels:
        chart_data_map[row] = {}
        for d in range(0,5):
            chart_data_map[row][str(d)] = 0

    for row in data:
        delay = (row.posting_date - row.due_date).days
		row.update({ "delay" : delay })
        if getdate(row.get('posting_date')).strftime("%B") == "January":


def execute(filters=None):
	if not filters.get("range1"):
		frappe.throw("Ageing 1 can not be Zero ot null")
	if not filters.get("range2"):
		frappe.throw("Ageing 2 can not be Zero ot null")
	if not filters.get("range3"):
		frappe.throw("Ageing 3 can not be Zero ot null")
	if not filters.get("range4"):
		frappe.throw("Ageing 4 can not be Zero ot null")
	data = []
	data = get_data_from_pe(filters)
    
	return data


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
		
        month_wise_data.update({getdate(row.posting_date).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.posting_date).strftime("%B_%Y"))) + 1})
        on_time_row.append(row)
		
	
		
    return on_time_row, 

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



def get_month_dates(year, month):
    # Start date is the 1st of the given month and year
    start_date = datetime(year, month, 1)
    # End date is the last day of the given month
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    return start_date, end_date
