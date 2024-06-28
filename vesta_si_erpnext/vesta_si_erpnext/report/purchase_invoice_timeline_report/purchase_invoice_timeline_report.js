// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Invoice Timeline Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		// {
		// 	'fieldname':"range1",
		// 	"label": __("Range 1"),
		// 	"fieldtype": "Int",
		// 	'default':30,
		// 	"reqd": 1
		// },
		// {
		// 	'fieldname':"range2",
		// 	"label": __("Range 2"),
		// 	"fieldtype": "Int",
		// 	'default':60,
		// 	"reqd": 1
		// },
		// {
		// 	'fieldname':"range3",
		// 	"label": __("Range 3"),
		// 	"fieldtype": "Int",
		// 	'default':90,
		// 	"reqd": 1
		// },
	]
};
