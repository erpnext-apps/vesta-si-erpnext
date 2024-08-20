import frappe
from frappe import _

def validate_iban(self,method):
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