import frappe
from frappe.utils import flt

def get_purchase_invoice_no(due_date):
    data = frappe.db.sql(f"""
                Select count(pi.name) as number_of_invoice, su.custom_payment_type
                From `tabPurchase Invoice` as pi
                Left Join `tabSupplier` as su ON su.name = pi.supplier
                Where pi.workflow_state in ('Approved','Approved by CEO','Partly Paid','Payment Ordered') and pi.status in ('Partly Paid','Unpaid','Overdue')
                and due_date < '{due_date}'
                Group By su.custom_payment_type
            """, as_dict=1)
    message = "<p>Hello P2P Team,</p><br>"
    message += "<p>As of today, {0}, the following purchase invoices are now overdue. Please process the payment through the upcoming ⁠payment run <a href = '{1}/app/payment-run'>Payment Run(click here)</a></p>".format(frappe.utils.formatdate(due_date, "dd MMMM, YYYY"), frappe.utils.get_url())

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
    message += "<br><br><p>Thanks & Regards</p>"

    frappe.sendmail(recipients = ["viral@fosserp.com", "vignesh@fosserp.com"],
			subject = 'Due Payment Process Detail',
			message = message)


#trigger email on monday and thursday

def send_email_():
    from frappe.utils import getdate, add_days, today
    from datetime import datetime
    currenct_day = getdate().strftime("%A")
    if currenct_day == "Monday":
        due_date = add_days(today(), 2)
        get_purchase_invoice_no(due_date)
    if currenct_day == "Thursday":
        due_date = add_days(today(), 2)
        get_purchase_invoice_no(due_date)


    