import frappe
import json
from frappe.utils import getdate
from datetime import datetime
import calendar



@frappe.whitelist()
def get_data(filters=None):
    filters = json.loads(filters)
    from vesta_si_erpnext.vesta_si_erpnext.report.pi_on_payment.pi_on_payment import execute
    fiscal_year = int(filters.get("fiscal_year"))
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
    start_date, end_date = get_month_dates(fiscal_year, month_number.get(filters.get('month')))
    filters.update({"from_date" : str(getdate(start_date)), "to_date" : str(getdate(end_date))})
    columns, data, A, charts = execute(filters)
    return charts.get('data')


def get_month_dates(year, month):
    # Start date is the 1st of the given month and year
    start_date = datetime(year, month, 1)
    # End date is the last day of the given month
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    return start_date, end_date

# January
# February
# March
# April
# May
# June
# July
# August
# September
# October
# November
# December