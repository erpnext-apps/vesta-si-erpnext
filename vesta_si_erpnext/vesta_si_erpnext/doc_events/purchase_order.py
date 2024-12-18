import frappe
from frappe.utils import now
from datetime import datetime
from vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_invoice import validate_currency

def validate(self , method):
    validate_currency(self)
    if currency := frappe.db.get_value("Supplier", self.supplier, "default_currency"):
        if currency != self.currency:
            frappe.throw("Supplier base currency is {0}, Kindly create an invoice in <b>{0}</b>. Or Create new supplier with billing currency {1}".format(currency, self.currency))
    if not self.custom_level_1_approval_pending and self.workflow_state =="Level 1 Approval Pending":
        self.custom_level_1_approval_pending = now()
    if not self.custom_level_2_approval_pending and self.workflow_state == "Level 2 Approval Pending":
        self.custom_level_2_approval_pending = now()
    if not self.custom_approved and self.workflow_state == "Approved":
        self.custom_approved = now()
    if not self.custom_approved_and_reviewed and self.workflow_state == "Approved and Reviewed":
        self.custom_approved_and_reviewed = now()
    if not self.custom_rejected and self.workflow_state == "Rejected":
        self.custom_rejected = now()
