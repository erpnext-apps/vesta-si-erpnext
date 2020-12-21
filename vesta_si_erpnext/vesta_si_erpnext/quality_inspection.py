# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext

def accept_reject_inspection(doc, method=None):
	print("in here =>", method)
	if any(reading.status == "Rejected" for reading in doc.readings):
		doc.status = "Rejected"
