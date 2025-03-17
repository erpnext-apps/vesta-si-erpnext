// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Budget without VAT"] = {
	"filters": [
		{
			fieldname : "project",
			label : "Project",
			fieldtype : "Link",
			options : "Project"
   		},
		{
			fieldname : "status",
			label : "PI Status",
			fieldtype : "Select",
			options : [
				"",
				"Paid",
				"Partly Paid",
				"Unpaid",
				"Overdue",
				]
		}
	]
};
