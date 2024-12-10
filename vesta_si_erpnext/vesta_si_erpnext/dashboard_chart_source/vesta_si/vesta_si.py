import frappe
from frappe import _

@frappe.whitelist()
def get_data(chart_name=None,
            chart=None,
            no_cache=None,
            filters=None,
            from_date=None,
            to_date=None,
            timespan=None,
            time_interval=None,
            heatmap_year=None,):
    label = ['a', 'b']
    data = [[1, 2], [3,4]]
    return {
		"labels": label,
		"datasets": [{"name": _("Stock Value"), "values": data, "chartType": "bar"}],
		"type": "bar",
	}