# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json

def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	columns = get_column(filters)
	return columns, data


def get_data(filters):
	fields = ['bank_giro_number', 'bank_name','plus_giro_number', 'bank_code', 'iban_code', 'bank_bic']
	label = {
		"bank_giro_number" : "Bank Giro Number",
		"bank_name" : "Bank Name",
		"plus_giro_number" : "Plush Giro Number",
		"bank_code" : "BBAN",
		"iban_code" : "IBAN CODE",
		"bank_bic" : "Bank Bic"
	}
	condition = ''
	if filters.get("supplier"):
		condition += f" and su.name = '{filters.get('supplier')}'"
	
	if filters.get("modified_by"):
		condition += f" and v.owner = '{filters.get('modified_by')}'"

	if filters.get("owner"):
		condition += f" and su.owner = '{filters.get('owner')}'"

	if filters.get("from_date"):
		condition += f" and v.creation >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		condition += f" and v.creation <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f"""
		Select su.name,v.data as v_data,v.owner,v.creation, su.owner as su_owner, su.creation as su_creation
		From `tabSupplier` as su 
		Left Join `tabVersion` as v ON v.docname = su.name and ref_doctype = "Supplier"
		where su.docstatus = 0 {condition}
	""",as_dict=1)
	
	final_data = []

	for row in data:
		if row.get("v_data"):
			version = json.loads(row.get('v_data'))
			if version.get("changed"):
				for d in version.get('changed'):
					if d[0] in fields:
						final_data.append({
							"name":row.name,
							"fieldname":label.get(d[0]),
							"old_value" : d[1],
							"new_value" : d[-1],
							"modified_by": frappe.db.get_value("User",row.owner, 'full_name'),
							"su_owner" : frappe.db.get_value("User",row.su_owner, 'full_name'),
							"updated_on":row.creation,
							"su_creation":row.su_creation

						})

	return final_data

def get_column(filters):
	columns = [
		{
			"fieldname":"name",
			"fieldtype" : "Link",
			"label":"Supplier",
			"options":"Supplier",
			"width":200
		},
		{
			"fieldname":"fieldname",
			"fieldtype" : "Data",
			"label":"Field Name",
			"width":200
		},
		{
			"fieldname":"old_value",
			"fieldtype" : "Data",
			"label":"Old Value",
			"width":200
		},
		{
			"fieldname":"new_value",
			"fieldtype" : "Data",
			"label":"New Value",
			"width":200
		},
		{
			"fieldname":"modified_by",
			"fieldtype" : "Data",
			"label":"Modified By",
			"width":200
		},
		{
			"fieldname":"updated_on",
			"fieldtype" : "Datetime",
			"label":"Update ON",
			"width":200
		},
		{
			"fieldname":"su_owner",
			"fieldtype" : "Data",
			"label":"Created By",
			"width":200
		},
		{
			"fieldname":"su_creation",
			"fieldtype" : "Datetime",
			"label":"Created On",
			"width":200
		},

		

	]
	return columns