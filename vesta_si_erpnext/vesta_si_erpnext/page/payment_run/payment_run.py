import frappe

@frappe.whitelist()
def get_purchase_invoice(due_date=None, payable_account=None, currency=None):
    if due_date:    
        data = frappe.db.sql(f"""
                Select name, bill_no, grand_total, outstanding_amount, supplier_name, workflow_state, supplier
                From `tabPurchase Invoice` 
                Where docstatus = 1 and outstanding_amount > 0 and due_date <= '{due_date}' and currency = '{currency}'
        """,as_dict=1)
        return {"invoices" : data}