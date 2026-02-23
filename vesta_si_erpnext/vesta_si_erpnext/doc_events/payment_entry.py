import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import get_negative_outstanding_invoices
from frappe.utils import get_link_to_form, comma_and, flt
from frappe.utils import (
    add_days,
    add_months,
    cint,
    comma_and,
    flt,
    fmt_money,
    formatdate,
    get_last_day,
    get_link_to_form,
    getdate,
    nowdate,
    today,
)
from frappe.desk.form.load import get_attachments


def validate(self, method):
    currency_list = []    
    if self.party_type == "Supplier":
        for row in self.references:
            currency_list.append(frappe.db.get_value(row.reference_doctype , row.reference_name , 'currency'))

        if len(list(set(currency_list))) > 1:
            frappe.throw("Purchase Invoices have different currencies. All selected purchase invoices must have the same currency.")
        elif list(set(currency_list)) and self.paid_from_account_currency != list(set(currency_list))[0] and self.custom_payment_run_type != 'Cross Border Payments (OTHER)':
            frappe.throw(f"Account Paid From should be in <b>{list(set(currency_list))[0]}<b>")
        party_account_currency = frappe.db.get_value("Account", self.paid_to, 'account_currency')
        
        company_currency = frappe.db.get_value("Company", self.company, 'default_currency')
        
        if self.payment_type == "Pay" and self.party_type == "Supplier":
            data = get_negative_outstanding_invoices(
                    "Supplier", 
                    self.party, 
                    self.paid_to, 
                    party_account_currency, 
                    company_currency,
                    condition = '')

            final_data = []
            for row in data:
                if not row.voucher_no in ["ACC-PINV-2024-00250-1", "ACC-PINV-2024-00251-1"]:
                    final_data.append(row)
                    
            if len(final_data):
                for row in data:
                    message = "Debit Note and Payment Entry available against this supplier {0}<br>".format(get_link_to_form(self.party_type, self.party))
                    message +="First reconcile those entry, reference available as mentioned below"
                    message += "<br><br>"
                    message += """<table width='100%'>"""
                    for row in data:
                        message += "<tr><td>{0}</td><td>{1} {2}</td></tr>".format(get_link_to_form(row.voucher_type, row.voucher_no),self.paid_to_account_currency, row.outstanding_amount)
                    message += "</table>"
                frappe.msgprint(message)
        if len(self.references):
            if self.references[0].reference_doctype == "Purchase Invoice":
                doc = frappe.get_doc("Purchase Invoice", self.references[0].reference_name)
                get_advance_entries(doc)
    copy_attachment_from_po_pi(self)

def get_advance_entries(self):
    res = self.get_advance_entries(
            include_unallocated=not cint(self.get("only_include_allocated_payments"))
        )
    if res and not self.allocate_advances_automatically:
        if not len(self.advances):
            frappe.throw("Advance payments available against supplier <b>{0}</b> <br> Enable <b>'Set Advances and Allocate (FIFO)'</b> or click on the <b>'Get Advances Paid'</b> button under the payments section.".format(self.supplier))

def on_submit(self, method):
    if self.party_type == "Supplier" and self.payment_type == "Pay":
        if not (self.custom_is_manual_payment_process or self.custom_xml_file_generated):
            frappe.throw("XML file is not generated for this payment entry <b>{0}</b>.".format(self.name))
        data =  frappe.db.sql(f'''
                Select parent From `tabPayment Transaction Log` 
                Where payment_entry = "{self.name}"
            ''', as_dict =1)
        flag = True
        if len(data):
            pel_doc = frappe.get_doc('Payment Export Log', data[0].parent)
            for row in pel_doc.logs:
                if row.payment_entry == self.name:
                    frappe.db.set_value(row.doctype , row.name, 'status', 'Submitted')
                
            pel_doc = frappe.get_doc('Payment Export Log', data[0].parent)
            for row in pel_doc.logs:
                if row.status == "Draft":
                    flag = False
            if flag:
                pel_doc = frappe.get_doc('Payment Export Log', data[0].parent)
                pel_doc.status = "Submitted"
                pel_doc.save()


def on_cancel(self, method):
    if self.payment_type == "Pay" and self.party_type == "Supplier":
        for row in self.references:
            if row.reference_doctype == "Purchase Invoice" and row.reference_name:
                doc = frappe.get_doc("Purchase Invoice", row.reference_name)
                frappe.db.set_value("Purchase Invoice", row.reference_name, "workflow_state", "Approved")

import os
import frappe
from frappe.desk.form.load import get_attachments
from frappe.utils import get_site_path


def file_exists_on_disk(file_url):
    if not file_url:
        return False

    file_url = file_url.lstrip("/")  # remove leading slash
    file_path = get_site_path(file_url)
    return os.path.exists(file_path)


def copy_attachment_from_po_pi(self):
    if not self.references:
        return

    for ref in self.references:
        if ref.reference_doctype not in ("Purchase Invoice", "Purchase Order"):
            continue

        attached_files = get_attachments(
            ref.reference_doctype,
            ref.reference_name
        )

        for file_row in attached_files:
            # 1️⃣ Check if File record already exists for this Payment Entry
            exists_in_pe = frappe.db.exists(
                "File",
                {
                    "file_url": file_row.file_url,
                    "attached_to_doctype": "Payment Entry",
                    "attached_to_name": self.name,
                },
            )

            # 2️⃣ If record exists AND physical file exists → skip
            if exists_in_pe and file_exists_on_disk(file_row.file_url):
                continue

            # 3️⃣ Attach file again (missing on disk or not linked)
            try:
                new_file = frappe.get_doc({
                    "doctype": "File",
                    "file_name": file_row.file_name,
                    "file_url": file_row.file_url,
                    "attached_to_doctype": "Payment Entry",
                    "attached_to_name": self.name,
                })
                new_file.insert(ignore_permissions=True)
            except:
                frappe.log_error("File is not exists", self.name)
