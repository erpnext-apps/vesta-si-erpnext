import frappe

def set_due_date_after_submit(self, method):
    if self.docstatus == 1:
        frappe.db.set_value("Purchase Invoice", self.name, 'due_date', self.payment_schedule[-1].due_date)
        self.reload()