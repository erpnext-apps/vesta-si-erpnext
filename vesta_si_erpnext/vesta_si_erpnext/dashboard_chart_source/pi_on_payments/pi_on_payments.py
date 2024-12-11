# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt
from frappe import _
import json

@frappe.whitelist()
def prepare_chart(filters =None):
    filters = json.loads(filters)
    if filters.get("fiscal_year"):
        doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
        year_start_date = doc.year_start_date
        year_end_date = doc.year_end_date
        filters.update({
            "from_date" : str(year_start_date),
            "to_date" : str(year_end_date)
        })

    data = execute(filters)


    if filters.get("range1"):
        label1 = "{0} - {1}".format(0, filters.get("range1"))
    if filters.get("range2"):
        label2 = "{0} - {1}".format(filters.get("range1") + 1, filters.get("range2"))
    if filters.get("range3"):
        label3 = "{0} - {1}".format(filters.get("range2") + 1, filters.get("range3"))
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
        chart_data_map[row]["{0}_ontime".format(row)] = 0
        for d in range(0,5):
            chart_data_map[row][str(d)] = 0
            
    for row in data:
        if getdate(row.get('posting_date')).strftime("%B") == "January":
            if flt(row.delay) <= 0:
                chart_data_map["January"]["January_ontime"] = chart_data_map["January"]["January_ontime"] + 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["January"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["January"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["January"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["January"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["January"]['4'] += 1
                
        if getdate(row.get('posting_date')).strftime("%B") == "February":
            if flt(row.delay) <= 0:
                chart_data_map["February"]["February_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["February"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["February"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["February"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["February"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["February"]['4'] += 1
        
        if getdate(row.get('posting_date')).strftime("%B") == "March":
            if flt(row.delay) <= 0:
                chart_data_map["March"]["March_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["March"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["March"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["March"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["March"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["March"]['4'] += 1

        if getdate(row.get('posting_date')).strftime("%B") == "April":
            if flt(row.delay) <= 0:
                chart_data_map["April"]["April_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["April"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["April"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["April"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["April"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["April"]['4'] += 1
        
        if getdate(row.get('posting_date')).strftime("%B") == "May":
            if flt(row.delay) <= 0:
                chart_data_map["May"]["May_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["May"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["May"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["May"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["May"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["May"]['4'] += 1
        
        if getdate(row.get('posting_date')).strftime("%B") == "June":
            if flt(row.delay) <= 0:
                chart_data_map["June"]["June_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["June"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["June"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["June"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["June"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["June"]['4'] += 1
        
        if getdate(row.get('posting_date')).strftime("%B") == "July":
            if flt(row.delay) <= 0:
                chart_data_map["July"]["July_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["July"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["July"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["July"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["July"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["July"]['4'] += 1
            
        if getdate(row.get('posting_date')).strftime("%B") == "August":
            if flt(row.delay) <= 0:
                chart_data_map["August"]["August_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["August"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["August"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["August"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["August"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["August"]['4'] += 1

        if getdate(row.get('posting_date')).strftime("%B") == "September":
            if flt(row.delay) <= 0:
                chart_data_map["September"]["September_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["September"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["September"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["September"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["September"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["September"]['4'] += 1
            
        if getdate(row.get('posting_date')).strftime("%B") == "October":
            if flt(row.delay) <= 0:
                chart_data_map["October"]["October_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["October"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["October"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["October"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["October"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["October"]['4'] += 1
        
        if getdate(row.get('posting_date')).strftime("%B") == "November":
            if flt(row.delay) <= 0:
                chart_data_map["November"]["November_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["November"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["November"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["November"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["November"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["November"]['4'] += 1

        if getdate(row.get('posting_date')).strftime("%B") == "December":
            if flt(row.delay) <= 0:
                chart_data_map["December"]["December_ontime"] += 1
            if 0 < row.delay <= flt(filters.get('range1')) :
                chart_data_map["December"]['0'] += 1
            if flt(filters.get('range1')) < flt(row.delay) <= flt(filters.get('range2')):
                chart_data_map["December"]['1'] += 1
            if flt(filters.get('range2')) < flt(row.delay) <= flt(filters.get('range3')):
                chart_data_map["December"]['2'] += 1
            if flt(filters.get('range3')) < flt(row.delay) <= flt(filters.get('range4')):
                chart_data_map["December"]['3'] += 1
            if flt(filters.get('range4')) < flt(row.delay):
                chart_data_map["December"]['4'] += 1
        
    return {
            "labels" : ["January" ,
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
                        "December" ],
            
            "datasets" : [
                {
                    'name': "On Time",
                    'values': [ chart_data_map["January"]["January_ontime"], chart_data_map["February"]["February_ontime"], chart_data_map["March"]["March_ontime"], chart_data_map["April"]["April_ontime"], chart_data_map["May"]["May_ontime"], chart_data_map["June"]["June_ontime"], chart_data_map["July"]["July_ontime"], chart_data_map["August"]["August_ontime"], chart_data_map["September"]["September_ontime"], chart_data_map["October"]["October_ontime"], chart_data_map["November"]["November_ontime"], chart_data_map["December"]["December_ontime"]],
                },
                {
                    'name': label1,
                    'values': [ chart_data_map["January"]["0"], chart_data_map["February"]["0"], chart_data_map["March"]["0"], chart_data_map["April"]["0"], chart_data_map["May"]["0"], chart_data_map["June"]["0"], chart_data_map["July"]["0"], chart_data_map["August"]["0"], chart_data_map["September"]["0"], chart_data_map["October"]["0"], chart_data_map["November"]["0"], chart_data_map["December"]["0"]],
                },
                {
                    'name': label2,
                    'values': [ chart_data_map["January"]["1"], chart_data_map["February"]["1"], chart_data_map["March"]["1"], chart_data_map["April"]["1"], chart_data_map["May"]["1"], chart_data_map["June"]["1"], chart_data_map["July"]["1"], chart_data_map["August"]["1"], chart_data_map["September"]["1"], chart_data_map["October"]["1"], chart_data_map["November"]["1"], chart_data_map["December"]["1"]],
                },
                {
                    'name': label3,
                    'values': [ chart_data_map["January"]["2"], chart_data_map["February"]["2"], chart_data_map["March"]["2"], chart_data_map["April"]["2"], chart_data_map["May"]["2"], chart_data_map["June"]["2"], chart_data_map["July"]["2"], chart_data_map["August"]["2"], chart_data_map["September"]["2"], chart_data_map["October"]["2"], chart_data_map["November"]["2"], chart_data_map["December"]["2"]],
                },
                {
                    'name': label4,
                    'values': [ chart_data_map["January"]["3"], chart_data_map["February"]["3"], chart_data_map["March"]["3"], chart_data_map["April"]["3"], chart_data_map["May"]["3"], chart_data_map["June"]["3"], chart_data_map["July"]["3"], chart_data_map["August"]["3"], chart_data_map["September"]["3"], chart_data_map["October"]["3"], chart_data_map["November"]["3"], chart_data_map["December"]["3"]],
                },
                {
                    'name': label5,
                    'values': [ chart_data_map["January"]["4"], chart_data_map["February"]["4"], chart_data_map["March"]["4"], chart_data_map["April"]["4"], chart_data_map["May"]["4"], chart_data_map["June"]["4"], chart_data_map["July"]["4"], chart_data_map["August"]["4"], chart_data_map["September"]["4"], chart_data_map["October"]["4"], chart_data_map["November"]["4"], chart_data_map["December"]["4"]],
                }
            ],
    }

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
        month_wise_data.update({getdate(row.posting_date).strftime("%B_%Y") : month_wise_data.get(str(getdate(row.posting_date).strftime("%B_%Y"))) + 1})
        on_time_row.append(row)
    
    return on_time_row

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
