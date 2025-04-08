import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_field():
    create_field = {
        "Role" : [
            {
                'fieldname' : "users",
                'label' : "Users",
                'fieldtype' : "Table MultiSelect",
                'options' : 'User Bucket',
                'insert_after' : 'restrict_to_domain'
            }
        ]
    }  
    create_custom_fields(create_field) 
    print("Field Created")