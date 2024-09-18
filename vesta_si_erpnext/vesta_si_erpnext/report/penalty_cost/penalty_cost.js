// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Penalty Cost"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.sys_defaults.year_start_date,
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname" : "expense_account",
			"label" : "Expense Head",
			"fieldtype" : "Select",
			"options" :["", "629301 - Reminder Fee & Penalty Cost (operational) - 9150", "824502 - Interest expense due to late payment - 9150"],
		}
	]
};
