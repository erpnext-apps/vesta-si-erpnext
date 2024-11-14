// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payment Delay Report"] = {
	"filters": [
		{
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.month_start(), -1),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.month_start(),-1),
			reqd: 1
		},
		{
			fieldname : "chart_type",
			label : "Chart Type",
			fieldtype : "Select",
			options : ["On Time Payments", "Delayed Payments"],
			default : "On Time Payments"
		}
	]
};