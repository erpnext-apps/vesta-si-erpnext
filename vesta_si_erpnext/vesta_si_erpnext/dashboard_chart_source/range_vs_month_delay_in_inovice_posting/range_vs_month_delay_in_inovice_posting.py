import frappe
import json
from frappe.utils import getdate, flt
from vesta_si_erpnext.vesta_si_erpnext.report.purchase_invoice_timeline_report.purchase_invoice_timeline_report import execute

@frappe.whitelist()
def get_data(filters=None):
    filters = json.loads(filters)
    if filters.get("fiscal_year"):
        doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
        year_start_date = doc.year_start_date
        year_end_date = doc.year_end_date
        filters.update({
            "from_date" : year_start_date,
            "to_date" : year_end_date
        })
    columns, data = execute(filters)

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

    january_range1 = 0
    january_range2 = 0
    january_range3 = 0
    january_range4 = 0
    january_range5 = 0

    month_number = {
        "January" : 1,
        "February" : 2,
        "March" : 3,
        "April" : 4,
        "May" : 5,
        "June" : 6,
        "July" : 7,
        "August" : 8, 
        "September" : 9, 
        "October" : 10,
        "November" : 11,
        "December" : 12
    }
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
        if flt(row.get("processing_days")) >= 1:
            if getdate(row.get('posting_date')).strftime("%B") == "January":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["January"]["0"] = chart_data_map["January"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["January"]["1"] = chart_data_map["January"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["January"]["2"] = chart_data_map["January"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["January"]["3"] = chart_data_map["January"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["January"]["4"] = chart_data_map["January"]["4"] + 1

            if getdate(row.get('posting_date')).strftime("%B") == "February":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["February"]["0"] = chart_data_map["February"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["February"]["1"] = chart_data_map["February"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["February"]["2"] = chart_data_map["February"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["February"]["3"] = chart_data_map["February"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["February"]["4"] = chart_data_map["February"]["4"] + 1

            if getdate(row.get('posting_date')).strftime("%B") == "March":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["March"]["0"] = chart_data_map["March"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["March"]["1"] = chart_data_map["March"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["March"]["2"] = chart_data_map["March"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["March"]["3"] = chart_data_map["March"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["March"]["4"] = chart_data_map["March"]["4"] + 1
            
            if getdate(row.get('posting_date')).strftime("%B") == "April":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["April"]["0"] = chart_data_map["April"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["April"]["1"] = chart_data_map["April"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["April"]["2"] = chart_data_map["April"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["April"]["3"] = chart_data_map["April"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["April"]["4"] = chart_data_map["April"]["4"] + 1
                
            if getdate(row.get('posting_date')).strftime("%B") == "May":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["May"]["0"] = chart_data_map["May"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["May"]["1"] = chart_data_map["May"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["May"]["2"] = chart_data_map["May"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["May"]["3"] = chart_data_map["May"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["May"]["4"] = chart_data_map["May"]["4"] + 1
            
            if getdate(row.get('posting_date')).strftime("%B") == "June":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["June"]["0"] = chart_data_map["June"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["June"]["1"] = chart_data_map["June"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["June"]["2"] = chart_data_map["June"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["June"]["3"] = chart_data_map["June"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["June"]["4"] = chart_data_map["June"]["4"] + 1
            
            if getdate(row.get('posting_date')).strftime("%B") == "July":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["July"]["0"] = chart_data_map["July"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["July"]["1"] = chart_data_map["July"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["July"]["2"] = chart_data_map["July"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["July"]["3"] = chart_data_map["July"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["July"]["4"] = chart_data_map["July"]["4"] + 1
            
            if getdate(row.get('posting_date')).strftime("%B") == "August":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["August"]["0"] = chart_data_map["August"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["August"]["1"] = chart_data_map["August"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["August"]["2"] = chart_data_map["August"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["August"]["3"] = chart_data_map["August"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["August"]["4"] = chart_data_map["August"]["4"] + 1

            if getdate(row.get('posting_date')).strftime("%B") == "September":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["September"]["0"] = chart_data_map["September"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["September"]["1"] = chart_data_map["September"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["September"]["2"] = chart_data_map["September"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["September"]["3"] = chart_data_map["September"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["September"]["4"] = chart_data_map["September"]["4"] + 1
            
            if getdate(row.get('posting_date')).strftime("%B") == "October":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["October"]["0"] = chart_data_map["October"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["October"]["1"] = chart_data_map["October"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["October"]["2"] = chart_data_map["October"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["October"]["3"] = chart_data_map["October"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["October"]["4"] = chart_data_map["October"]["4"] + 1

            if getdate(row.get('posting_date')).strftime("%B") == "November":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["November"]["0"] = chart_data_map["November"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["November"]["1"] = chart_data_map["November"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["November"]["2"] = chart_data_map["November"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["November"]["3"] = chart_data_map["November"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["November"]["2"] = chart_data_map["November"]["2"] + 1

            if getdate(row.get('posting_date')).strftime("%B") == "December":
                if 0 <= row.get("processing_days") <= filters.get("range1"):
                    chart_data_map["December"]["0"] = chart_data_map["December"]["0"] + 1
                if filters.get("range1") +1 <= row.get("processing_days") <= filters.get("range2"):
                    chart_data_map["December"]["1"] = chart_data_map["December"]["1"] + 1
                if filters.get("range2") +1 <= row.get("processing_days") <= filters.get("range3"):
                    chart_data_map["December"]["2"] = chart_data_map["December"]["2"] + 1
                if filters.get("range3") +1 <= row.get("processing_days") <= filters.get("range4"):
                    chart_data_map["December"]["3"] = chart_data_map["December"]["3"] + 1
                if filters.get("range4") +1 <= row.get("processing_days"):
                    chart_data_map["December"]["4"] = chart_data_map["December"]["4"] + 1


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
                'name': label1,
                'values': [ chart_data_map["January"]["0"], chart_data_map["February"]["0"], chart_data_map["March"]["0"], chart_data_map["April"]["0"], chart_data_map["May"]["0"], chart_data_map["June"]["0"], chart_data_map["July"]["0"], chart_data_map["August"]["0"], chart_data_map["September"]["0"], chart_data_map["October"]["0"], chart_data_map["November"]["0"], chart_data_map["December"]["0"]],
            },
            {
                'name': label2,
                'values': [ chart_data_map["January"]["1"], chart_data_map["February"]["1"], chart_data_map["March"]["1"], chart_data_map["April"]["1"], chart_data_map["May"]["1"], chart_data_map["June"]["1"], chart_data_map["July"]["1"], chart_data_map["August"]["1"], chart_data_map["September"]["1"], chart_data_map["October"]["1"], chart_data_map["November"]["1"], chart_data_map["December"]["1"]],
            },
            {
                'name': label3,
                'values': [chart_data_map["January"]["2"], chart_data_map["February"]["2"], chart_data_map["March"]["2"], chart_data_map["April"]["2"], chart_data_map["May"]["2"], chart_data_map["June"]["2"], chart_data_map["July"]["2"], chart_data_map["August"]["2"], chart_data_map["September"]["2"], chart_data_map["October"]["2"], chart_data_map["November"]["2"], chart_data_map["December"]["2"]],
            },
            {
                'name': label4,
                'values': [chart_data_map["January"]["3"], chart_data_map["February"]["3"], chart_data_map["March"]["3"], chart_data_map["April"]["3"], chart_data_map["May"]["3"], chart_data_map["June"]["3"], chart_data_map["July"]["3"], chart_data_map["August"]["3"], chart_data_map["September"]["3"], chart_data_map["October"]["3"], chart_data_map["November"]["3"], chart_data_map["December"]["3"]],
            },
            {
                'name': label5,
                'values': [chart_data_map["January"]["4"], chart_data_map["February"]["4"], chart_data_map["March"]["4"], chart_data_map["April"]["4"], chart_data_map["May"]["4"], chart_data_map["June"]["4"], chart_data_map["July"]["4"], chart_data_map["August"]["4"], chart_data_map["September"]["4"], chart_data_map["October"]["4"], chart_data_map["November"]["4"], chart_data_map["December"]["4"]],
            }
        ]
    }
            

        