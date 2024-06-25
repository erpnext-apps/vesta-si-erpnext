// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Overdue Invoice Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			'fieldname':"range1",
			"label": __("Range 1"),
			"fieldtype": "Int",
			'default':30,
			"reqd": 1
		},
		{
			'fieldname':"range2",
			"label": __("Range 2"),
			"fieldtype": "Int",
			'default':60,
			"reqd": 1
		},
		{
			'fieldname':"range3",
			"label": __("Range 3"),
			"fieldtype": "Int",
			'default':90,
			"reqd": 1
		},
		{
			'fieldname':"chart_type",
			"label": __("Chart Type"),
			"fieldtype": "Select",
			'options':['Pie', 'Bar', 'Line'],
			'default':'Pie'
		}
	]
};
