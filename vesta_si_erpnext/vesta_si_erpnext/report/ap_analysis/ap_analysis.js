// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["AP Analysis"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"document",
			"label": __("Document"),
			"fieldtype": "Select",
			"options" : ['','Purchase Invoice','Purchase Order'],
			on_change:()=>{
				frappe.query_report.set_filter_value("workflow_state", "");
			},
		},
		{
			"fieldname":"workflow_state",
			"label": __("Workflow State"),
			"fieldtype": "Link",
			"options" : "Workflow State",
			get_query: () => {
				var document = frappe.query_report.get_filter_value("document");
				return {
					query : "vesta_si_erpnext.vesta_si_erpnext.report.ap_analysis.ap_analysis.get_workflow_state",
					filters:{
						docname : document
					}
				};
			},
		}
	]
};
