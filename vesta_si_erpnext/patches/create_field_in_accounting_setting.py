import frappe

def execute():
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
    doc = frappe.new_doc("Role")
    doc.role_name = "Over Billing Approver"
    doc.insert()
