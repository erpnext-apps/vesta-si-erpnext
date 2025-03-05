import frappe

def execute():
    # Enable Validation in Purchase Receipt
    doc = frappe.new_doc("Custom Field")
    doc.dt = "Buying Settings"
    doc.label = "Same rate and qty validation for purchase receipt"
    doc.fieldtype = "Check"
    doc.insert_after = "use_transaction_date_exchange_rate"
    doc.fieldname = "enable_same_rate_validation"
    doc.is_system_generated = 1
    doc.module = "Vesta Si Erpnext"
    doc.description = "1) The rate and quantity should be the same as in the Purchase Order (PO).\n2)Changing the item code is not allowed, and no additional items that are not in the PO can be added."
    doc.insert()
    frappe.db.commit()
