import frappe

from vesta_si_erpnext.vesta_si_erpnext.page.payment_run.payment_run import get_purchase_invoice, get_invoices

def get_automation_of_payment_entry():
    payment_type = [
        "Domestic (Swedish) Payments (SEK)",
        "SEPA (EUR)",
        "Cross Border Payments (USD)",
        "Cross Border Payments (EUR)",
    ]
    for row in payment_type:
        purchase_invoices = get_purchase_invoice("ASC", row, due_date="2024-12-08")
        invoices = []
        for d in purchase_invoices.get('invoices'):
            if not d.workflow_state == "Blocked":
                invoices.append(d.name)
        get_invoices(str(invoices), row)