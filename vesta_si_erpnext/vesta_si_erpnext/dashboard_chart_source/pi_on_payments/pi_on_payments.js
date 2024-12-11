frappe.dashboards.chart_sources["PI On Payments"] = {
	method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.pi_on_payments.pi_on_payments.prepare_chart",
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
        {
			fieldname : "range1",
			label : "Ageing 1",
			fieldtype : "Int",
			default : 30
		},
		{
			fieldname : "range2",
			label : "Ageing 2",
			fieldtype : "Int",
			default : 60
		},
		{
			fieldname : "range3",
			label : "Ageing 3",
			fieldtype : "Int",
			default : 90
		},
		{
			fieldname : "range4",
			label : "Ageing 4",
			fieldtype : "Int",
			default : 120
		},
    ]
}