import frappe
from frappe.utils import now
from datetime import datetime

def validate(self , method):
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
