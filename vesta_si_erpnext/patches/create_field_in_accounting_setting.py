import frappe

def execute():
    meta = frappe.get_meta('Accounts Settings')
    if not meta.has_field('allowowerbillbyamount'):
        doc = frappe.new_doc("Custom Field")
        doc.dt = "Accounts Settings"
        doc.label = "Overbilling Settings Vesta-Si"
        doc.fieldtype = "Section Break"
        doc.insert_after = "credit_controller"
        doc.fieldname = "allowowerbillbyamount"
        doc.is_system_generated = 1
        doc.module = "Vesta Si Erpnext"
        doc.insert()
        frappe.db.commit()

    meta = frappe.get_meta('Accounts Settings')
    if not meta.has_field('overbill_allow_by_amount'):
        doc = frappe.new_doc("Custom Field")
        doc.dt = "Accounts Settings"
        doc.label = "Overbill Allow by Amount"
        doc.fieldtype = "Currency"
        doc.insert_after = "allowowerbillbyamount"
        doc.fieldname = "overbill_allow_by_amount"
        doc.is_system_generated = 1
        doc.module = "Vesta Si Erpnext"
        doc.insert()
        frappe.db.commit()

    meta = frappe.get_meta('Accounts Settings')
    if not meta.has_field('overbill_items'):
        doc = frappe.new_doc("Custom Field")
        doc.dt = "Accounts Settings"
        doc.label = "Allow Overbill Items"
        doc.fieldtype = "Table MultiSelect"
        doc.insert_after = "overbill_allow_by_amount"
        doc.fieldname = "overbill_items"
        doc.options = "Allow Overbill Item"
        doc.is_system_generated = 1
        doc.module = "Vesta Si Erpnext"
        doc.insert()


    #create a new role
    if not frappe.db.exists("Role", "Over Billing Approver"):
        doc = frappe.new_doc("Role")
        doc.role_name = "Over Billing Approver"
        doc.insert()