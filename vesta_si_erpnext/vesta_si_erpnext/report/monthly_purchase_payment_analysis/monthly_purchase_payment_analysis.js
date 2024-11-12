// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Purchase Payment Analysis"] = {
	"filters": [
		{
			fieldname:"payment_export_log",
			label: __("Payment Export Log"),
			fieldtype: "Link",
			options : "Payment Export Log",
			reqd: 0
		},
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
			options : ["On Time Payment", "Delayed Payment"],
			default : "On Time Payment"
		}
	]
};
