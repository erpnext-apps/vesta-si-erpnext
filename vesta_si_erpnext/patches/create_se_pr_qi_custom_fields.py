# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	item_fields = [
		dict(fieldname='inspection_col_break', fieldtype='Column Break',
			insert_after='inspection_required_before_delivery'),
		dict(fieldname='analysis_frequency', label='Analysis Frequency', fieldtype='Int',
			insert_after='inspection_col_break')
	]

	stock_entry_detail_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			 insert_after='col_break4', depends_on='eval:in_list(["Material Receipt", "Manufacture"], parent.purpose)'),
		dict(fieldname='analysis_required', label='Analysis Required', fieldtype='Check',
			 insert_after='quality_inspection')
	]

	purchase_receipt_item_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			 insert_after='include_exploded_items')
	]

	batch_fields = [
		dict(fieldname='supplier_bag_no', label='Supplier Bag No.', fieldtype='Data',
			insert_after='item_name', read_only=1)
	]

	qi_template_fields = [
		dict(fieldname='analysis_priority', label='Analysis Priority', fieldtype='Table',
			insert_after='inspection_template', options='Analysis Priority')
	]

	qi_fields = [
		dict(fieldname='analysis_frequency', label='Item Analysis Frequency', fieldtype='Int',
			insert_after='description', fetch_from='item_code.analysis_frequency', read_only=1),
		dict(fieldname='customer', label='Customer', fieldtype='Link', options='Customer',
			 insert_after='status'),
		dict(fieldname='product_analysis', label='Product Analysis', fieldtype='Check',
			 insert_after='sample_size'),
		dict(fieldname='analysis_summary', label='Analysis Summary', fieldtype='Section Break',
			insert_after='readings', depends_on='product_analysis'),
		dict(fieldname='run_analysis', label='Run Analysis', fieldtype='Button',
			insert_after='analysis_summary', depends_on="eval:doc.docstatus == 0"),
		dict(fieldname='analysed_item_code', label='Analysed Item Code', fieldtype='Link', options='Item',
			 insert_after='run_analysis'),
		dict(fieldname='inspection_summary_table', label='', fieldtype='Table',
			insert_after='analysed_item_code', options='Inspection Summary')
	]

	custom_fields = {
		"Item": item_fields,
		"Stock Entry Detail": stock_entry_detail_fields,
		"Purchase Receipt Item": purchase_receipt_item_fields,
		"Batch": batch_fields,
		"Quality Inspection Template": qi_template_fields,
		"Quality Inspection": qi_fields
	}

	create_custom_fields(custom_fields, update=True)

	make_property_setter("Quality Inspection", "quality_inspection_template", "read_only", 1, "Check")