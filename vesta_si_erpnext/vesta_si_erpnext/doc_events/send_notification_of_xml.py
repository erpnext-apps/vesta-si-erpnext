import frappe
from frappe.utils import flt, today, getdate, add_days, get_url, nowdate

def get_purchase_invoice_no(due_date):
    data = frappe.db.sql(f"""
                Select count(pi.name) as number_of_invoice, su.custom_payment_type
                From `tabPurchase Invoice` as pi
                Left Join `tabSupplier` as su ON su.name = pi.supplier
                Where pi.workflow_state in ('Approved','Approved by CEO','Partly Paid','Payment Ordered') and pi.status in ('Partly Paid','Unpaid','Overdue')
                and due_date <= '{due_date}'
                Group By su.custom_payment_type
            """, as_dict=1)
    message = "<p>Hello P2P Team,</p><br>"
    message += "<p>Good day!</p><br>"
    message += "<p>I hope this message finds you well.</p><br>"
    message += "<p>As of {0}, we need to process the invoice that is due by {1}. Please initiate the payment run by <a href = '{2}/app/payment-run'>clicking here</a></p>".format(frappe.utils.formatdate(str(getdate()), "dd MMMM, YYYY"),frappe.utils.formatdate(due_date, "dd MMMM, YYYY"), frappe.utils.get_url())

    message += """
    <table width = "100%" border= 1 style="border-collapse: collapse;" >
        <tr>
            <th width="5%" style="text-align:center;padding:5px;">SR</th>
            <th style="text-align:left; padding:5px;" width="45%"><p><b>Payment Type</p></b></th>
            <th style="text-align:center; padding:5px;" width="50%"><p><b>Number of Payments</p></b></th>
        </tr>
    """
    total_payment = 0
    d = 0
    for row in data:
        d += 1
        total_payment += row.number_of_invoice
        message += """
            <tr>
                <td style="text-align:center;padding:5px;">{2}</td>
                <td style="padding:5px;">{0}</td>
                <td align="center" style="padding:5px;">{1}</td>
            </tr>
        """.format(row.custom_payment_type, row.number_of_invoice, d)
    message += "<tr><td></td><td><b>Total</b></td><td align='center'><b>{0}</b></td></tr></table>".format(total_payment)
    message += "<br><p>This is a system-generated message based on our purchase invoice data.</p><br><p>Thanks & Regards</p>"

    notify_list = []
    user_list = frappe.db.get_list("User", pluck="name")
    for row in user_list:
        if "PE Notify(For XML)" in frappe.get_roles(row) and row != "Administrator":
            notify_list.append(row)

    if getdate().strftime('%A') == "Monday":
        subject = f"Action required 'Obetalda leverantörsfakturor' | Due By { getdate().strftime('%A') } { today() } | Processing till { getdate(add_days(today(), 2)).strftime('%A') } {str(getdate(add_days(today(), 2)))}."
    if getdate().strftime('%A') == "Thursday":
        subject = f"Action required 'Obetalda leverantörsfakturor' | Due By { getdate().strftime('%A') } { today() } | Processing till { getdate(add_days(today(), 3)).strftime('%A') } {str(getdate(add_days(today(), 3)))}."

  
    frappe.sendmail(recipients = notify_list,
			subject = subject,
			message = message
            )


# trigger email on monday and thursday

def send_email_():
    from frappe.utils import getdate, add_days, today
    from datetime import datetime
    currenct_day = getdate().strftime("%A")
    if currenct_day == "Monday":
        due_date = add_days(today(), 3)
        get_purchase_invoice_no(due_date)
    if currenct_day == "Thursday":
        due_date = add_days(today(), 4)
        get_purchase_invoice_no(due_date)


# from vesta_si_erpnext.vesta_si_erpnext.doc_events.send_notification_of_xml import get_purchase_invoice_no