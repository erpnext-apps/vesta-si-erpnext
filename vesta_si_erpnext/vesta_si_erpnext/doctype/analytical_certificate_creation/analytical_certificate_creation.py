# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AnalyticalCertificateCreation(Document):
	def validate(doc):
		qty = 0
		for item in doc.batches:
			qty += item.weight
		doc.qty = qty


@frappe.whitelist()
def get_quality_inspection_info(batch_no):
	return frappe.get_last_doc("Quality Inspection", filters = {"batch_no": batch_no, 'docstatus': 1})

