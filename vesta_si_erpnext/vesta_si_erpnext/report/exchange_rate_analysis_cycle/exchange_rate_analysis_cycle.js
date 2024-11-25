// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Exchange Rate Analysis Cycle"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date"), // change this before version update --> erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_end_date"), // change this before version update --> erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
			reqd: 1,
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "MultiSelectList",
			options : [
				{'description' : '', "value":'Draft'},
				{'description' : '', "value":'Return'},
				{'description' : '', "value":'Debit Note Issued'},
				{'description' : '', "value":'Submitted'},
				{'description' : '', "value":'Paid'},
				{'description' : '', "value":'Partly Paid'},
				{'description' : '', "value":'Unpaid'},
				{'description' : '', "value":'Overdue'},
				{'description' : '', "value":'Cancelled'},
				{'description' : '', "value":'Internal Transfer'}
			],
			width:200
		}
	]
};
