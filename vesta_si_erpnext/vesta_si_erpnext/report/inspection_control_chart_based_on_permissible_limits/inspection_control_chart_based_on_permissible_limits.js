// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Inspection Control Chart Based On Permissible Limits"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
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
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				return {
					filters: {
						"has_batch_no": 1
					}
				};
			},
			"reqd":1
		},
		{
			"fieldname":"qi_parameter",
			"label": __("QI Parameter"),
			"fieldtype": "Link",
			"options": "Quality Inspection Parameter",
		}
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data.max_value < data.reading_1){
			value = value.replace('<a ', '<a style="color: red;" ')
			value = "<span style='color:red'>" + value + "</span>";
		}
		if(data.min_value > data.reading_1){
			value = value.replace('<a ', '<a style="color: red;" ')
			value = "<span style='color:red'>" + value + "</span>";
		}
			
		return value
	}
};
