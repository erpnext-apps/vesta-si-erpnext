import frappe 
import json
from frappe.utils import getdate
from datetime import datetime
import calendar


@frappe.whitelist()
def get_data(filters):
    filters = json.loads(filters)
    from vesta_si_erpnext.vesta_si_erpnext.report.pi_on_payment.pi_on_payment import execute
    month_number = {
        "January" : 1,
        "February" : 2,
        "March" : 3,
        "April" : 4,
        "May" : 5,
        "June" : 6,
        "July" : 7,
        "August" : 8, 
        "September" : 9, 
        "October" : 10,
        "November" : 11,
        "December" : 12
    }
    labels = [
        "January" ,
        "February" ,
        "March" ,
        "April" ,
        "May" ,
        "June" ,
        "July" ,
        "August" , 
        "September" , 
        "October" ,
        "November" ,
        "December" 
    ]

    fiscal_year = int(filters.get("fiscal_year"))
    on_time_values = []
    delay_values = []
    for row in labels:

        start_date, end_date = get_month_dates(fiscal_year, int(month_number.get(row)))

        filters.update({
            "from_date" : str(getdate(start_date)), 
            "to_date" : str(getdate(end_date)),
            "range1" : 30,
            "range2" : 60,
            "range3" :  90,
            "range4" : 120
            })

        filters.update( {"chart_type" : "Payments On Time"} )
        columns, data, A, on_time_charts = execute(filters)
        on_time_values.append(on_time_charts.get("data").get("datasets")[0].get("values")[0])

        filters.update( {"chart_type" : "Payments On Delay"} )
        columns, data, A, delay_charts = execute(filters)
        delay_values.append(sum(delay_charts.get("data").get("datasets")[0].get("values")[1:]))

    
    return {
			"labels": ["On Time Payment", "Delay Time Payment"],
			"datasets": [{"name": "Delay", "values": [sum(on_time_values), sum(delay_values)]}],
		}

def get_month_dates(year, month):
    # Start date is the 1st of the given month and year
    start_date = datetime(year, month, 1)
    # End date is the last day of the given month
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    return start_date, end_date