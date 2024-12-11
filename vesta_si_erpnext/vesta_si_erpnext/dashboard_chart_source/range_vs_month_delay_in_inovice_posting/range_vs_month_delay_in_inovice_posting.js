frappe.dashboards.chart_sources["Range Vs Month Delay In Inovice Posting"] = {
	method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.range_vs_month_delay_in_inovice_posting.range_vs_month_delay_in_inovice_posting.get_data",
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
			default: frappe.sys_defaults.fiscal_year // change after update
        },
        {
			fieldname:"from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date"),
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_end_date"),
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
};