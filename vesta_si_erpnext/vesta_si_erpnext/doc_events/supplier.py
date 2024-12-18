import frappe
from frappe import _

def validate_iban(self,method):
    validate_currency_and_payment_type(self)
    
    """
    Algorithm: https://en.wikipedia.org/wiki/International_Bank_Account_Number#Validating_the_IBAN
    """
    # IBAN field is optional
    if not self.iban_code:
        return

    def encode_char(c):
        # Position in the alphabet (A=1, B=2, ...) plus nine
        return str(9 + ord(c) - 64)

    # remove whitespaces, upper case to get the right number from ord()
    iban = "".join(self.iban_code.split(" ")).upper()

    # Move country code and checksum from the start to the end
    flipped = iban[4:] + iban[:4]

    # Encode characters as numbers
    encoded = [encode_char(c) if ord(c) >= 65 and ord(c) <= 90 else c for c in flipped]

    try:
        to_check = int("".join(encoded))
    except ValueError:
        frappe.throw(_("IBAN is not valid"))

    if to_check % 97 != 1:
        frappe.throw(_("IBAN is not valid"))
    

def validate_currency_and_payment_type(self):
    if self.custom_payment_type == 'Cross Border Payments (OTHER)':
        return
    if  self.default_currency == "SEK" and self.custom_payment_type != "Domestic (Swedish) Payments (SEK)":
        frappe.throw(f"If the selected billing currency is <b>'{self.default_currency}'</b>, the payment type must be <b>'Domestic (Swedish) Payments (SEK).</b>'")

    if  self.default_currency == "EUR" and self.custom_payment_type not in  ['SEPA (EUR)', 'Cross Border Payments (EUR)']:
        frappe.throw(f"If the selected billing currency is <b>'{self.default_currency}'</b>, the payment type must be <b>'SEPA (EUR)'</b> or <b>'Cross Border Payments (EUR)'</b>")
    
    if self.default_currency == "USD" and self.custom_payment_type != 'Cross Border Payments (USD)':
        frappe.throw(f"If the selected billing currency is <b>'{self.default_currency}'</b>, the payment type must be <b>'Cross Border Payments (USD)'</b>")

    on_change_of_payment_type(self) #Do not Deployee


def on_change_of_payment_type(self):
    old_doc = self.get_doc_before_save()

    if old_doc.custom_payment_type != self.custom_payment_type:
        frappe.msgprint(str("gl_entry"))
        gl_entry = frappe.db.get_list("Purchase Invoice", { "supplier" : self.name, "docstatus" : 1 }, "name")
        if gl_entry:
            frappe.throw("Supplier is link with transactions, kindly create a new supplier for different currency or different payment type")
    

        