// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Tag-Based Purchase Order Insights"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("Start Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
		},
		{
			fieldname: "to_date",
			label: __("End Date"),
			fieldtype: "Date",
			default: frappe.datetime.nowdate(),
		},
	]
};
