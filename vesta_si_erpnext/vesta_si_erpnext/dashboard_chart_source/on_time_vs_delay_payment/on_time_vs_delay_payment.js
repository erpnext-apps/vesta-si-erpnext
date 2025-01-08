frappe.dashboards.chart_sources["On Time Vs Delay payment"] = {
	method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.on_time_vs_delay_payment.get_data",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		},
        {
            fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.sys_defaults.fiscal_year
        },
	]
};