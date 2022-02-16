# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
	custom_fields = {
		'Stock Entry': [
			dict(fieldname='custom_apply_putaway_rule', label='Custom Apply Putaway Rule',
				fieldtype='Check', hidden=1, insert_after='apply_putaway_rule')
		],

		'Purchase Receipt': [
			dict(fieldname='custom_apply_putaway_rule', label='Custom Apply Putaway Rule',
				fieldtype='Check', hidden=1, insert_after='apply_putaway_rule')
		],
	}

	create_custom_fields(custom_fields, update=True)