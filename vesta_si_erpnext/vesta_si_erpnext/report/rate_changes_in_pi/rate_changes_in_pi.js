// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rate Changes in PI"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname" : "item_code",
			"label" : __("Item Code"),
			"fieldtype" : "Link",
			"options" : "Item",
			"width": "80",
		},
		{
			"fieldname" : "purchase_invoice",
			"label" : __("Purchase Invoice"),
			"fieldtype" : "Link",
			"options" : "Purchase Invoice",
			"width": "80",
		},
		{
			"fieldname" : "supplier",
			"label" : __("Supplier"),
			"fieldtype" : "Link",
			"options" : "Supplier",
			"width": "80",
		},
		{
			"fieldname" : "group_by",
			"label" : __("Group By"),
			"fieldtype" : "Select",
			"options" : "\nItem Code\nPurchase Invoice\nSupplier",
			"width": "80",
		}
	]
};
