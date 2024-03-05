import frappe

def validate(self, method):
    currency_list = []    
    if self.party_type == "Supplier":
        for row in self.references:
            currency_list.append(frappe.db.get_value(row.reference_doctype , row.reference_name , 'currency'))

        if len(list(set(currency_list))) > 1:
            frappe.throw("Purchase Invoices have different currencies. All selected purchase invoices must have the same currency.")
        elif self.paid_from_account_currency != list(set(currency_list))[0]:
            frappe.throw(f"Account Paid From should be in <b>{list(set(currency_list))[0]}<b>")