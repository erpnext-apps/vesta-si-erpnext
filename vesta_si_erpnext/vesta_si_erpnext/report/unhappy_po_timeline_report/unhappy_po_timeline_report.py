# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from datetime import date


def execute(filters=None):
	columns, data = [], []
	data = get_version_data(filters)
	columns = get_columns(filters)
	return columns, data


def get_version_data(filters):

	conditions = ''
	if filters.get("from_date"):
		conditions += f" and po.transaction_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.transaction_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name, po.creation, po.transaction_date, v.owner, v.creation as versioncreation
		from `tabPurchase Order` as po 
		left join `tabVersion` as v on po.name = v.docname
		where data like '%workflow_state%' and ref_doctype = 'Purchase Order' {conditions}
		order by docname
	""",as_dict = 1)
	log = []

	for row in data:
		version = {}
		d = json.loads(row.data)
		for r in d.get('changed'):
			print(r[-1])
			if r[0] == 'workflow_state' and r[-1] == 'Approved':
				version.update({
					'purchase_order':row.name,
					'creation':row.creation,
					'posting_date':row.transaction_date,
					'approval_user':row.owner,
					"versioncreation":row.versioncreation,
					"days": (row.versioncreation - row.creation).days
				})
				log.append(version)
				break
		continue

	user_data = frappe.db.sql(f""" 
		Select name , full_name
		from `tabUser`
	""",as_dict = 1)
	map_user = {}
	for row in user_data:
		map_user[row.name] = row.full_name
	
	for row in log:
		if map_user.get(row.get('approval_user')):
			row.update({'approval_user':map_user.get(row.get('approval_user'))})


	return log

def get_columns(filters):
	columns =[
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 180,
		},
		{
			"label": _("Creation Date"),
			"fieldname": "creation",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Approver name "),
			"fieldname": "approval_user",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Approve time"),
			"fieldname": "versioncreation",
			"fieldtype": "Datetime",
			"options": "currency",
			"width": 180,
		},
		{
			"label": _("Days"),
			"fieldname": "days",
			"fieldtype": "Data",
			"width": 100,
		}

	]
	return columns