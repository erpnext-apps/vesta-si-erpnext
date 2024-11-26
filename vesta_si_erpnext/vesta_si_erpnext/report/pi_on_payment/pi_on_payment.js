// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PI on Payment"] = {
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
			options : ["Payment On Time", "Payments On Delay"],
			default : "Payment On Time"
		},
		{
			fieldname : "range1",
			label : "Ageing 1",
			fieldtype : "Data",
			default : 30
		},
		{
			fieldname : "range2",
			label : "Ageing 2",
			fieldtype : "Data",
			default : 60
		},
		{
			fieldname : "range3",
			label : "Ageing 3",
			fieldtype : "Data",
			default : 90
		},
		{
			fieldname : "range4",
			label : "Ageing 4",
			fieldtype : "Data",
			default : 120
		}
	]
};
