# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from datetime import date
from frappe.utils import flt, getdate


def execute(filters=None):
	columns, data = [], []
	data, chart = get_version_data(filters)
	columns = get_columns(filters)
	return columns, data, None, chart


def get_version_data(filters):

	conditions = ''
	if filters.get("from_date"):
		conditions += f" and po.transaction_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.transaction_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name, po.creation, po.transaction_date, v.owner, v.creation as versioncreation, po.owner
		from `tabPurchase Order` as po 
		left join `tabVersion` as v on po.name = v.docname
		where data like '%workflow_state%' and ref_doctype = 'Purchase Order' {conditions}
		order by docname
	""",as_dict = 1)
	log = []
	processing_days = 0
	days = 0
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
					"days": (row.versioncreation - row.creation).days,
					"processing_days": (getdate(row.creation) - row.transaction_date).days,
					'created_by' : frappe.db.get_value("User", row.owner, 'full_name')
				})
				log.append(version)
				processing_days += (getdate(row.creation) - row.transaction_date).days
				days += (row.versioncreation - row.creation).days
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
	labels = []
	chart_log = {}
	for row in log:
		if row.get('approval_user') not in labels:
			labels.append(row.get('approval_user'))
		if not chart_log.get(row.get('approval_user')):
			chart_log[row.get('approval_user')] = []
			chart_log[row.get('approval_user')].append(flt(row.get('days')))
		else:
			chart_log[row.get('approval_user')].append(flt(row.get('days')))
	row_ =[]
	for row in labels:
		row_.append(sum(chart_log.get(row)))

	chart = {
		"data": {
						'labels': labels,
						'datasets': [
							{
								'name': 'Number of Day to Approve',
								'values': row_,
								'type': 'pie',
							},					
						]
					},
					'type': 'pie',
					'height': 250,
	}
	length = len(log)
	if length:
		log.insert(0, {"purchase_order":"<b>Average</b>","processing_days" : processing_days/length, "days" : days/length})
	return log , chart

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
			"label": _("Processing Days"),
			"fieldname": "processing_days",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Approver name "),
			"fieldname": "approval_user",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Approved date"),
			"fieldname": "versioncreation",
			"fieldtype": "Datetime",
			"options": "currency",
			"width": 180,
		},
		{
			"label": _("Number of day for approval"),
			"fieldname": "days",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Created By"),
			"fieldname": "created_by",
			"fieldtype": "Data",
			"width": 100,
		}

	]
	return columns