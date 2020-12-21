# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	stock_entry_detail_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			 insert_after='col_break4', depends_on='eval:parent.purpose =="Material Receipt"')
	]

	purchase_receipt_item_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			 insert_after='include_exploded_items')
	]

	batch_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			insert_after='item_name')
	]

	qi_template_fields = []

	qi_fields = []

	custom_fields = {
		"Stock Entry Detail": stock_entry_detail_fields,
		"Purchase Receipt Item": purchase_receipt_item_fields,
		"Batch": batch_fields,
		"Quality Inspection Template": qi_template_fields,
		"Quality Inspection": qi_fields
	}

	create_custom_fields(custom_fields, update=True)
