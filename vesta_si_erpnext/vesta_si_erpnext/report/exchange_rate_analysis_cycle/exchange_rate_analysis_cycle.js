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
	]
};
