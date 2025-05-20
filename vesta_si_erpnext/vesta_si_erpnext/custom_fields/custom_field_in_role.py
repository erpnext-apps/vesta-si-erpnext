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
        ],
        "Buying Settings" : [
            {
                'fieldname' : "enable_todo_email_for_purchase_invoice",
                'label' : "Enable ToDo Emails for Purchase Invoice",
                'fieldtype' : "Check",
                'insert_after' : 'use_transaction_date_exchange_rate'
            }
        ],
        "Item" : [
            {
                'fieldname' : "max_amount_allow",
                'label' : "Maximum Amount Allow in Purchase Order (Update Item)",
                'fieldtype' : "Currency",
                'insert_after' : 'overbill_allow_by_amount'
            }
        ]
    }  
    create_custom_fields(create_field) 
    
    print("Field Created")