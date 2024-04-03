# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class PaymentExportLog(Document):
	pass


@frappe.whitelist()
def submit_all_payment_entry(self : dict):
	doc = json.loads(self)
	log = frappe.get_doc('Payment Export Log', doc.get('name'))
	for row in log.logs:
		payment_doc = frappe.get_doc('Payment Entry', row.get('payment_entry'))
		payment_doc.submit()
		frappe.db.set_value("Payment Transaction Log", row.get('name'), 'status', payment_doc.status)
	frappe.db.set_value('Payment Export Log', doc.get('name'), 'status', 'Submitted')
	frappe.msgprint('Payment Entry Succesfully Submited')
