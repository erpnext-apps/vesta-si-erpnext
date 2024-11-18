# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from vesta_si_erpnext.vesta_si_erpnext.report.purchase_invoice_timeline_report.purchase_invoice_timeline_report import execute as report_execution
from frappe.utils import flt, getdate

def execute(filters=None):
	columns, data = [], []
	columns, data = report_execution(filters)
	columns = [
		{
			"fieldname" : "month",
			"fieldtype" : "Data",
			"label" : "Month",
			"width" : 150
		},
		{
			"fieldname" : "proce_days",
			"fieldtype" : "Int",
			"label" : "Delay In Invoice Creation",
			"width" : 200
		},
		{
			"fieldname" : "processing_days",
			"fieldtype" : "Int",
			"label" : "Delay In Processing Days",
			"width" : 200
		},
		{
			"fieldname" : "proce_days_posting",
			"fieldtype" : "Int",
			"label" : "Delay In Posting",
			"width" : 200
		},
		{
			"fieldname" : "creation_percentage",
			"fieldtype" : "Data",
			"label" : "Creation(%)",
			"precision" : 2,
			"width" : 200
		},
		{
			"fieldname" : "posting_percentage",
			"fieldtype" : "Data",
			"label" : "Posting(%)",
			"precision" : 2,
			"width" : 200
		}

	]

	january_row = []
	february_row = []
	march_row = []
	april_row = []
	may_row = [] 
	june_row = []
	july_row = []
	august_row = []
	september_row = []
	october_row = []
	november_row = []
	december_row = []

	january_proce_days, january_proce_days_posting , january_processing_days = 0, 0, 0
	february_proce_days, february_proce_days_posting, february_processing_days = 0, 0, 0
	march_proce_days, march_proce_days_posting , march_processing_days= 0, 0, 0
	april_proce_days, april_proce_days_posting , april_processing_days= 0, 0, 0
	may_proce_days, may_proce_days_posting , may_processing_days= 0, 0, 0 
	june_proce_days, june_proce_days_posting , june_processing_days= 0, 0, 0
	july_proce_days, july_proce_days_posting , july_processing_days= 0, 0, 0
	august_proce_days, august_proce_days_posting , august_processing_days = 0, 0, 0
	september_proce_days, september_proce_days_posting, september_processing_days = 0, 0, 0
	october_proce_days, october_proce_days_posting ,october_processing_days= 0, 0, 0
	november_proce_days, november_proce_days_posting , november_processing_days= 0, 0, 0
	december_proce_days, december_proce_days_posting, december_processing_days= 0, 0, 0

	for row in data:
		if flt(row.get('processing_days')) < 0:
			if getdate(row.get('posting_date')).month == 1:
				january_row.append(row)
				january_proce_days += flt(row.get('proce_days'))
				january_proce_days_posting += flt(row.get('proce_days_posting'))
				january_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 2:
				february_row.append(row)
				february_proce_days += flt(row.get('proce_days'))
				february_proce_days_posting += flt(row.get('proce_days_posting'))
				february_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 3:
				march_row.append(row)
				march_proce_days += flt(row.get('proce_days'))
				march_proce_days_posting += flt(row.get('proce_days_posting'))
				march_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 4:
				april_row.append(row)
				april_proce_days += flt(row.get('proce_days'))
				april_proce_days_posting += flt(row.get('proce_days_posting'))
				april_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 5:
				may_row.append(row)
				may_proce_days += flt(row.get('proce_days'))
				may_proce_days_posting += flt(row.get('proce_days_posting'))
				may_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 6:
				june_row.append(row)
				june_proce_days += flt(row.get('proce_days'))
				june_proce_days_posting += flt(row.get('proce_days_posting'))
				june_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 7:
				july_row.append(row)
				july_proce_days += flt(row.get('proce_days'))
				july_proce_days_posting += flt(row.get('proce_days_posting'))
				july_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 8:
				august_row.append(row)
				august_proce_days += flt(row.get('proce_days'))
				august_proce_days_posting += flt(row.get('proce_days_posting'))
				august_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 9:
				september_row.append(row)
				september_proce_days += flt(row.get('proce_days'))
				september_proce_days_posting += flt(row.get('proce_days_posting'))
				september_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 10:
				october_row.append(row)
				october_proce_days += flt(row.get('proce_days'))
				october_proce_days_posting += flt(row.get('proce_days_posting'))
				october_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 11:
				november_row.append(row)
				november_proce_days += flt(row.get('proce_days'))
				november_proce_days_posting += flt(row.get('proce_days_posting'))
				november_processing_days += flt(row.get('processing_days'))
				continue
			if getdate(row.get('posting_date')).month == 12:
				december_row.append(row)
				december_proce_days += flt(row.get('proce_days'))
				december_proce_days_posting += flt(row.get('proce_days_posting'))
				december_processing_days += flt(row.get('processing_days'))
				continue

	monthly_data = [
			{'month' : 'January', "proce_days" : january_proce_days , "proce_days_posting" : january_proce_days_posting, "processing_days": january_processing_days , 
			"creation_percentage" : round((january_proce_days / (january_proce_days + january_proce_days_posting)) * 100, 2)  if january_proce_days_posting else 0,
			"posting_percentage" : round((january_processing_days / (january_proce_days + january_proce_days_posting)) * 100, 2)  if january_proce_days_posting else 0
			}, 
			{'month' : 'February', "proce_days" : february_proce_days, "proce_days_posting": february_proce_days_posting , "processing_days": february_processing_days , 
			"creation_percentage" : round((february_proce_days / (february_proce_days+february_proce_days_posting)) * 100, 2)  if february_proce_days_posting else 0 ,
			"posting_percentage" : round((february_processing_days / (february_proce_days+february_proce_days_posting)) * 100, 2)  if february_proce_days_posting else 0
			}, 
			{'month' : 'March', "proce_days" : march_proce_days, "proce_days_posting":  march_proce_days_posting, "processing_days": march_processing_days , 
			"creation_percentage" : round((march_proce_days / (march_proce_days_posting + march_proce_days)) * 100, 2)  if march_proce_days_posting else 0,
			"posting_percentage" : round((march_processing_days / (march_proce_days_posting + march_proce_days)) * 100, 2)  if march_proce_days_posting else 0
			}, 
			{'month' : 'April', "proce_days" : april_proce_days, "proce_days_posting":  april_proce_days_posting, "processing_days": april_processing_days , 
			"creation_percentage" : round((april_proce_days / (april_proce_days + april_proce_days_posting)) * 100, 2)  if april_proce_days_posting else 0,
			"posting_percentage" : round((april_processing_days / (april_proce_days + april_proce_days_posting)) * 100, 2)  if april_proce_days_posting else 0
			}, 
			{'month' : 'May', "proce_days" : may_proce_days, "proce_days_posting":  may_proce_days_posting, "processing_days": may_processing_days , 
			"creation_percentage" : round((may_proce_days / (may_proce_days + may_proce_days_posting)) * 100, 2)  if may_proce_days_posting else 0,
			"posting_percentage" : round((may_processing_days / (may_proce_days + may_proce_days_posting)) * 100, 2)  if may_proce_days_posting else 0
			}, 
			{'month' : 'June', "proce_days" : june_proce_days, "proce_days_posting":  june_proce_days_posting, "processing_days": june_processing_days , 
			"creation_percentage" : round((june_proce_days / (june_proce_days + june_proce_days_posting)) * 100, 2)  if june_proce_days_posting else 0 ,
			"posting_percentage" : round((june_processing_days / (june_proce_days + june_proce_days_posting)) * 100, 2)  if june_proce_days_posting else 0
			}, 
			{'month' : 'July', "proce_days" : july_proce_days, "proce_days_posting": july_proce_days_posting , "processing_days": july_processing_days , 
			"creation_percentage" : round((july_proce_days / (july_proce_days + july_proce_days_posting)) * 100, 2)  if july_proce_days_posting else 0,
			"posting_percentage" : round((july_processing_days / (july_proce_days + july_proce_days_posting)) * 100, 2)  if july_proce_days_posting else 0
			}, 
			{'month' : 'August', "proce_days" : august_proce_days, "proce_days_posting": august_proce_days_posting , "processing_days": august_processing_days , 
			"creation_percentage" : round((august_proce_days/(august_proce_days + august_proce_days_posting)) * 100, 2)  if august_proce_days_posting else 0,
			"posting_percentage" : round((august_processing_days / (august_proce_days + august_proce_days_posting)) * 100, 2)  if august_proce_days_posting else 0
			}, 
			{'month' : 'September', "proce_days" : september_proce_days, "proce_days_posting": september_proce_days_posting , "processing_days": september_processing_days , 
			"creation_percentage" : round((september_proce_days/(september_proce_days + september_proce_days_posting)) * 100, 2)  if september_proce_days_posting else 0,
			"posting_percentage" : round((september_processing_days / (september_proce_days + september_proce_days_posting)) * 100, 2)  if september_proce_days_posting else 0
			}, 
			{'month' : "October", "proce_days" : october_proce_days, "proce_days_posting": october_proce_days_posting , "processing_days": october_processing_days , 
			"creation_percentage" : round((october_proce_days/(october_proce_days_posting + october_proce_days)) * 100, 2)  if october_proce_days_posting else 0,
			"posting_percentage" : round((october_processing_days / (october_proce_days_posting + october_proce_days)) * 100, 2)  if october_proce_days_posting else 0
			}, 
			{'month' : "November", "proce_days" : november_proce_days, "proce_days_posting": november_proce_days_posting , "processing_days": november_processing_days , 
			"creation_percentage" : round((november_proce_days/(november_proce_days+november_proce_days_posting)) * 100, 2)  if november_proce_days_posting else 0,
			"posting_percentage" : round((november_processing_days / (november_proce_days+november_proce_days_posting)) * 100, 2)  if november_proce_days_posting else 0
			}, 
			{'month' : "December", "proce_days" : december_proce_days, "proce_days_posting": december_proce_days_posting, "processing_days":  december_processing_days , 
			"creation_percentage" : round((december_proce_days/(december_proce_days+december_proce_days_posting)) * 100, 2)  if december_proce_days_posting else 0,
			"posting_percentage" : round((december_processing_days / (december_proce_days+december_proce_days_posting)) * 100, 2)  if  december_proce_days_posting else 0
			},
		]

	label = [
		"January",
		"February",
		"March",
		"April",
		"May" ,
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",	
		]
	
	value1 = [
		january_proce_days,
		february_proce_days, 
		march_proce_days, 
		april_proce_days, 
		may_proce_days, 
		june_proce_days,
		july_proce_days, 
		august_proce_days, 
		september_proce_days, 
		october_proce_days, 
		november_proce_days, 
		december_proce_days
	]

	value2 = [ 
		january_processing_days ,
		 february_processing_days, 
		march_processing_days,
		 april_processing_days,
		 may_processing_days ,
		june_processing_days,
		 july_processing_days,
		 august_processing_days, 
		 september_processing_days ,
		october_processing_days,
		 november_processing_days,
		 december_processing_days
	]

	chart = {
			
			"data": {
					'labels': label,
					'datasets': [
						{
							'name': 'Delay In Invoice Creation',
							'values': value1,
							'chartType': 'bar',
						},
						{
							'name': 'Delay In Processing',
							'values': value2,
							'chartType': 'bar',
						}
					]
				},
				"type": "bar",
			}

	return columns, monthly_data, None, chart
