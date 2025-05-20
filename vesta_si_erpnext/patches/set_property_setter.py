
import frappe


def execute():
    set_fieldtype_to_phone()


def set_fieldtype_to_phone():
    frappe.get_doc({
        "doctype": "Property Setter",
        "doctype_or_field": "DocField",
        "doc_type": "Accounts Settings",  
        "field_name": "overbill_allow_by_amount",
        "property": "hidden",
        "value": "1",
        "property_type": "Check",
        "is_system_generated":1
    }).insert(ignore_permissions=True)
    frappe.clear_cache(doctype="Patient Encounter")