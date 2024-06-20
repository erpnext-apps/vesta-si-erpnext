import frappe
import json
from frappe.utils import nowdate, getdate, flt
import datetime
import calendar

def install_pandas():
    try:
        import pandas
        print("Pandas is already installed.")
    except ImportError:
        print("Pandas is not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "pandas"])
            print("Pandas has been successfully installed.")
        except Exception as e:
            print("Error occurred while installing Pandas:", e)

@frappe.whitelist()
def get_penalty_cost_paid_suppliers(filters):
    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(nowdate(),as_dict =1)

    from_date = str(current_year.year_start_date)
    to_date = str(current_year.year_end_date)

    filters = json.loads(filters)
    cond = ''
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
    cond += f" and pi.posting_date >= '{from_date}'"
    cond += f" and pi.posting_date <= '{to_date}'"
    data = frappe.db.sql(f"""
            Select count(pi.supplier) as number_of_supplier
            from `tabPurchase Invoice` as pi
            left join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
            where pi.docstatus = 1  {cond}
            Group By pi.supplier
        """,as_dict = True) 
    
    return {
                "value": flt(len(data)),
                "fieldtype": "Float",
            }

@frappe.whitelist()
def get_total_penalty_cost_remitted_to_suppliers(filters):
    filters = json.loads(filters)

    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(nowdate(),as_dict =1)

    from_date = str(current_year.year_start_date)
    to_date = str(current_year.year_end_date)

    cond = ''
    if filters.get('company'):
        cond += f" and pi.company = '{filters.get('company')}'"
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
    
    cond += f" and pi.posting_date >= '{from_date}'"

    cond += f" and pi.posting_date <= '{to_date}'"
    data = frappe.db.sql(f"""
            Select sum(pii.base_net_amount) as base_net_amount, pi.name, pii.expense_account
            From `tabPurchase Invoice` as pi
            left Join `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
            Where pi.docstatus = 1 {cond}
    """,as_dict = 1)
    return {
                "value": flt(data[0].get('base_net_amount')) if data else 0,
                "fieldtype": "Currency",
            }

@frappe.whitelist()
def get_total_penalty_cost_remitted_to_suppliers_monthly(filters):
    filters = json.loads(filters)
    current_date = getdate()
    from_date = current_date.replace(day=1)
    to_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])

    cond = ''
    if filters.get('company'):
        cond += f" and pi.company = '{filters.get('company')}'"
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
   
    cond += f" and pi.posting_date >= '{from_date}'"

    cond += f" and pi.posting_date <= '{to_date}'"
    data = frappe.db.sql(f"""
            Select sum(pii.base_net_amount) as base_net_amount, pi.name
            From `tabPurchase Invoice` as pi
            left Join `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
            Where pi.docstatus = 1 {cond}
    """,as_dict = 1)
    return {
                "value": data[0].get('base_net_amount') if data and data[0].get('base_net_amount') else 0,
                "fieldtype": "Currency",
            }