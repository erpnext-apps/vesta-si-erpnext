# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from frappe.utils import get_link_to_form

class PaymentExportLog(Document):
	def on_update(self):
		flag = True
		for row in self.logs:
			if row.status != "Submitted":
				flag = False
		if flag:
			self.db_set('status', "Submitted")


@frappe.whitelist()
def submit_all_payment_entry(self : dict):
	doc = json.loads(self)
	skipped = []
	log = frappe.get_doc('Payment Export Log', doc.get('name'))
	flag = False
	for row in log.logs:
		if not row.ignore_to_submit_payment_entry:
			payment_doc = frappe.get_doc('Payment Entry', row.get('payment_entry'))
			if payment_doc.get('difference_amount') > 0 or payment_doc.get('difference_amount') < 0:
				frappe.throw(f"Difference amount should be <b>Zero</b> {get_link_to_form('Payment Entry',row.get('payment_entry'))}")
			payment_doc.submit()
			frappe.db.set_value("Payment Transaction Log", row.get('name'), 'status', payment_doc.status)
			flag = True
	if flag:
		frappe.msgprint("Payment Entry has been submitted succesfully")

