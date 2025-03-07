import frappe


def execute():
    #create a custom field in purchase receipt
    meta = frappe.get_meta('Item')
    if not meta.has_field('overbill_allow_by_amount'):
        doc = frappe.new_doc("Custom Field")
        doc.dt = "Item"
        doc.label = "Allowed Overbilling Amount (SEK)"
        doc.fieldtype = "Currency"
        doc.insert_after = "over_billing_allowance"
        doc.fieldname = "overbill_allow_by_amount"
        doc.is_system_generated = 1
        doc.module = "Vesta Si Erpnext"
        doc.insert()