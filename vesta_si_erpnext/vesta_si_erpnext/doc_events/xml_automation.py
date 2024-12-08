import frappe
from vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export import get_payments, generate_payment_file
from frappe.utils import today

def get_payment_entry():
    payment_export_settings = get_payment_export_settings()
    payment_type = [
        "Domestic (Swedish) Payments (SEK)",
        "SEPA (EUR)",
        "Cross Border Payments (USD)",
        "Cross Border Payments (EUR)",
    ]
    for row in payment_type:
        data = get_payments(row, payment_export_settings)
        payments = data.get("payments")
        payments_ = []
        for d in payments:
            payments_.append(d.get("name"))
        if payments_:
            xml_content = generate_payment_file(str(payments_), payment_export_settings, today(), row)
            content = xml_content.get("content")
            print(content)
            file_name = "output.xml"
            try:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"XML file '{file_name}' generated successfully!")
            except Exception as e:
                print(f"An error occurred: {e}")

def get_payment_export_settings():
    return frappe.db.get_list("Payment Export Settings", pluck="name")[0]

# from vesta_si_erpnext.vesta_si_erpnext.doc_events.xml_automation import get_payment_entry