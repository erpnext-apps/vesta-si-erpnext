import frappe
from frappe.utils import (
	get_link_to_form
)


def get_pending_invoice():
    workflow_details = frappe.db.get_list("Workflow", {'is_active' : 1, "document_type" : 'Purchase Invoice'}, "name")

    workflow_map = {}

    doc = frappe.get_doc("Workflow", workflow_details[0].name)

    state_for_email = []
    role = []
    
    for row in doc.transitions:
        if row.action == "Approve" and row.state != "Draft":
            workflow_map[row.state]  =  row
            state_for_email.append(row.state)
            role.append(row.allowed)

    for row in state_for_email:
        data = frappe.db.sql(f""" 
                    Select name, workflow_state, supplier_name, grand_total, due_date
                    From `tabPurchase Invoice`
                    Where workflow_state = '{row}' and workflow_state != 'Blocked'
        """, as_dict=1)
        if not data:
            continue
        role = workflow_map.get(row).get('allowed')
        html  = "<p>This is a gentle reminder to review and approve the following Purchase Invoices that are currently pending your approval:</p><br>"
        html += """
            <table width="100%" border=1 class="table">
                <tr>
                    <td align="center"><b>Invoice Id</b></td>
                    <td align="center"><b>Due Date</b></td>
                    <td align="center"><b>Supplier Name</b></td>
                    <td align="center"><b>Status</b></td>
                </tr>
            """
        role_doc = frappe.get_doc("Role", role)
        for pi in data:
            html += """
                <tr>
                    <td align="left">{0}</td>
                    <td align="left">{1}</td>
                    <td align="left">{2}</td>
                    <td align="left">{4}</td>
                </tr>
            
            """.format(get_link_to_form("Purchase Invoice", pi.name), pi.due_date, pi.supplier_name, pi.grand_total, pi.workflow_state)
        html += "</table>"
        html += "<p>Your timely approval will help us ensure that vendor payments are processed smoothly and <span style='background-color:03ffff;'>on time to avoid any interest cost or penalty cost.</span></p>"
        html += "<p>Thank you for your attention to this matter.</p>"
        email_recipient = [row.user for row in role_doc.users]
        email_recipient.append("vignesh@fosserp.com")
        email_recipient.append("p2p.vestasi@skf.com")
        frappe.sendmail(
            recipients=email_recipient,
            subject="Reminder: Pending Approval for Purchase Invoices",
            message=html
        )


        

def get_users_by_role(role_name):
    users = frappe.db.sql("""
        SELECT parent as name 
        FROM `tabHas Role` 
        WHERE role = %s
    """, (role_name,), as_dict=True)
    return [user["name"] for user in users]
    