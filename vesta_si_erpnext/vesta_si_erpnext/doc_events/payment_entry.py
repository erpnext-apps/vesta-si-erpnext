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


def on_submit(self, method):
    data =  frappe.db.sql(f'''
            Select parent From `tabPayment Transaction Log` 
            Where payment_entry = "{self.name}"
        ''', as_dict =1)
    
    pel_doc = frappe.get_doc('Payment Export Log', data[0].parent)
    flag = True
    for row in pel_doc.logs:
        if row.payment_entry == self.name:
            frappe.db.set_value(row.doctype , row.name, 'status', 'Submitted')
        if row.status != "Submitted":
            flag = False
    if flag:
        frappe.db.set_value('Payment Export Log', data[0].parent , 'status', 'Submitted')
