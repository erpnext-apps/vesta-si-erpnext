frappe.dashboards.chart_sources["January PI On Payment"] = {
	method: "vesta_si_erpnext.vesta_si_erpnext.dashboard_chart_source.january_pi_on_payment.january_pi_on_payment.get_data",
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
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today())
        },
		{
			fieldname : "chart_type",
			label : "Chart Type",
			fieldtype : "Select",
			options : ["Payment On Time", "Payments On Delay"],
			default : "Payment On Time"
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
		{
			fieldname : "month",
			label : "Month",
			fieldtype : "Select",
			options : ["January",
				"February",
				"March",
				"April",
				"May",
				"June",
				"July",
				"August",
				"September",
				"October",
				"November",
				"December"]
		}
	]
};