import frappe
from vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export import get_payments, generate_payment_file
from frappe.utils import flt, today, getdate, add_days, get_url, nowdate, now
from frappe.desk.form.load import get_attachments
from vesta_si_erpnext.vesta_si_erpnext.doc_events.sftp_transfer import Sftp


# # Create an instance of the Sftp class
@frappe.whitelist()
def get_payment_entry(payments, payment_export_settings, posting_date, payment_type, bank_account = None):
    sftp = frappe.get_doc("SFTP Credential")
    hostname = sftp.hostname
    username = sftp.username
    password = sftp.password
    remote_path = sftp.remote_path    # Replace with your remote path
    port = 22

    payment_export_settings = get_payment_export_settings()
    payment_type = [
        "Domestic (Swedish) Payments (SEK)",
        "SEPA (EUR)",
        "Cross Border Payments (USD)",
        "Cross Border Payments (EUR)",
    ]
    # for row in payment_type:
        # data = get_payments(row, payment_export_settings)
        # payments = data.get("payments")
        # payments_ = []
        # for d in payments:
        #     payments_.append(d.get("name"))
    if payments:
        xml_content = generate_payment_file(payments, payment_export_settings, posting_date, payment_type, bank_account)
        content = xml_content.get("content")
        url = get_url().replace("https://", '')
        file_name = "{1}/private/files/payments{0}.xml".format(str(getdate()).replace("_", "").replace(" ", "").replace("-", ''), url)
        file_name = file_name.replace(" ", "-").replace("_", "")
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(content)
        except Exception as e:
            frappe.msgprint(f"An error occurred: {e}")
        
        pel = frappe.db.get_list("Payment Export Log", pluck="name")[0]

        new_file = frappe.new_doc("File")
        new_file.file_url = file_name.replace(f"{url}", '')
        new_file.attached_to_doctype = "Payment Export Log"
        new_file.attached_to_name = pel
        new_file.is_private = 1
        new_file.save()
        frappe.db.commit()
        if sftp.enabled:
            main_path = "/home/frappe/frappe-bench/sites/{0}".format(url)
            file_url = get_attechment_paths(pel)
            local_file = main_path + file_url
            remote_path = "/in/payments" 
            sftp_instance = Sftp(
                hostname=hostname,
                username=username,
                local_file=local_file,
                remote_path=remote_path,
                password=password,
                port=port
            )
            try:
                sftp_instance.sftp_upload()
                message = "XML file transferred to Nomentia.<br>The payment entry has been submitted automatically."
                frappe.msgprint(message)
            except Exception as e:
                frappe.msgprint(f"An error occurred: {e}")


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

        