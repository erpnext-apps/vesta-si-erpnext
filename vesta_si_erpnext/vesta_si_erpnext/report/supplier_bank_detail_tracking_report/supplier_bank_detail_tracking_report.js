// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Bank Detail Tracking Report"] = {
	"filters": [
			{
				"fieldname":"from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"width": "80"
			},
			{
				"fieldname":"to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
			},
			{
				"fieldname":"supplier",
				"fieldtype" : "Link",
				"label":"Supplier",
				"options":"Supplier"
			},
			{
				"fieldname":"modified_by",
				"fieldtype" : "Link",
				"label":"Modified By",
				"options":"User"
			},
			{
				"fieldname":"owner",
				"fieldtype" : "Link",
				"label":"Created By",
				"options":"User"
			},
	]
};
