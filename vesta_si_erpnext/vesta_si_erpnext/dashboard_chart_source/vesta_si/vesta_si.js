frappe.dashboards.chart_sources["Vesta Si"] = {
	method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.vesta_si.vesta_si.get_data",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		}
	]
};