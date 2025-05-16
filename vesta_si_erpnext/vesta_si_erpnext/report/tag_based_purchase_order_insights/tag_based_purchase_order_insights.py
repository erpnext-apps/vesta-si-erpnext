# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe


def execute(filters={"from_date":"2025-04-14","to_date":"2025-05-14"}):
	columns, data = [], []
	columns = [
		{
			"fieldname" : "owner",
			"fieldtype" : "Link",
			"Label" : "User",
			"options" : "User"
		},
		{
			"fieldname" : "document_name",
			"fieldtype" : "Dynamic Link",
			"Label" : "Document Name",
			"options" : "document_type"
		},
		{
			"fieldname" : "document_type",
			"fieldtype" : "Data",
			"Label" : "Document Type",
		},
		{
			"fieldname" : "tag",
			"fieldtype" : "Data",
			"Label" : "Tag",
		}
	]
	condition = ''
	if filters.get("from_date"):
		condition += f" and creation >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		condition += f" and creation <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f"""
				SELECT owner, document_name, document_type, tag
				From `tabTag Link`
				Where 1=1 {condition}
				""", as_dict= 1)


	return columns, data



