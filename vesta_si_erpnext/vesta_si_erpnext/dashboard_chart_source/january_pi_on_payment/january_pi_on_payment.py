import frappe
import json

@frappe.whitelist()
def get_data(filters=None):
    filters = json.loads(filters)
    from vesta_si_erpnext.vesta_si_erpnext.report.pi_on_payment.pi_on_payment import execute
    fiscal_year = filters.get("fiscal_year")
    start_date, end_date = get_january_dates(fiscal_year)
    filters.update({"from_date" : str(getdate(start_date)), "to_date" : str(getdate(end_date))})
    columns, data, A, charts = execute(filters)
    return charts


def get_january_dates(year):
    # Start date: January 1st
    start_date = datetime(year, 1, 1)
    # End date: January 31st
    end_date = datetime(year, 1, 31)
    return start_date, end_date