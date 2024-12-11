import frappe
from vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export import get_payments, generate_payment_file
from frappe.utils import today
from frappe.desk.form.load import get_attachments
from vesta_si_erpnext.vesta_si_erpnext.doc_events.sftp_transfer import Sftp

hostname = "52.157.97.77"
username = "cm-skftest-12"
password = "*EklmvpLlzV!.xKt7rTsd7Mh"
remote_path = "/in/payments/"     # Replace with your remote path
port = 22

# # Create an instance of the Sftp class

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
            
            file_name = "vesta/public/files/payments{0}.xml".format(xml_content.get("time"))
            try:
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"XML file '{file_name}' generated successfully!")
            except Exception as e:
                print(f"An error occurred: {e}")
            
            pel = frappe.db.get_list("Payment Export Log", pluck="name")[0]

            new_file = frappe.new_doc("File")
            new_file.file_url = file_name.replace("vesta/public", '')
            new_file.attached_to_doctype = "Payment Export Log"
            new_file.attached_to_name = pel
            new_file.save()
            frappe.db.commit()
            main_path = "/home/ubuntu/frappe-bench/sites/vesta/public/"
            file_url = get_attechment_paths(pel)
            local_file = main_path + file_url
            remote_path = "/in/payments/" 
            sftp_instance = Sftp(
                hostname=hostname,
                username=username,
                local_file=local_file,
                remote_path=remote_path,
                password=password,
                port=port
            )
            sftp_instance.sftp_upload()





def get_payment_export_settings():
    return frappe.db.get_list("Payment Export Settings", pluck="name")[0]

# from vesta_si_erpnext.vesta_si_erpnext.doc_events.xml_automation import get_payment_entry
def get_attechment_paths(pel):
    doc = frappe.get_doc("Payment Export Log", pel)
    attachment = get_attachments(doc.doctype, doc.name)
    for row in attachment:
        extension = get_extension(row.file_url)
        if extension == ".xml":
            return row.file_url


def get_extension(path):
    import os
    file_path = path
    extension = os.path.splitext(file_path)[1]
    return extension

        