frappe.dashboards.chart_sources[ "GRIR Monthly Chart" ] = {
    method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.grir_monthly_chart.giri_monthly_chart.get_giri_data",
    filters: [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Link",
            options : "Fiscal Year",
            default : erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),

 		},
              
	]
};