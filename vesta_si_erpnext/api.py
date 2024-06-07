import frappe
import json


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
    filters = json.loads(filters)
    cond = ''
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
    if filters.get('from_date'):
        cond += f" and pi.posting_date >= '{filters.get('from_date')}'"
    if filters.get('to_date'):
        cond += f" and pi.posting_date <= '{filters.get('to_date')}'"
    data = frappe.db.sql(f"""
            Select count(pi.supplier) as number_of_supplier
            from `tabPurchase Invoice` as pi
            left join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
            where pi.docstatus = 1  {cond}
            Group By pi.supplier
        """,as_dict = True) 
    
    return {
                "value": len(data),
                "fieldtype": "Float",
            }