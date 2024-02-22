# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from datetime import date


def execute(filters=None):
	columns, data = [], []
	columns , data = get_version_data(filters)
	return columns, data


def get_version_data(filters):

	conditions = ''
	if filters.get("from_date"):
		conditions += f" and po.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.posting_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name as purchase_invoice, po.creation, po.posting_date, v.owner, v.creation as versioncreation , v.docname
		from `tabPurchase Invoice` as po 
		left join `tabVersion` as v on po.name = v.docname
		where data like '%workflow_state%' and ref_doctype = 'Purchase Invoice' {conditions}
		order by docname , v.creation
	""",as_dict = 1)
	log = []
	workflow = frappe.get_doc('Workflow', {'document_type' : "Purchase Invoice" , 'is_active':1})
	workstate_list = []
	for row in workflow.transitions:
		workstate_list.append(row.next_state)
		if row.next_state == "Approved":
			break

	version = {}
	state_counter = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth']
	
	state_list = []
	for row in data:
		d = json.loads(row.data)
		for r in d.get('changed'):
			if r[-1] not in state_list and r[-1] in workstate_list:
				state_list.append(r[-1])
			if r[0] == "workflow_state" and r[-1] in workstate_list:
				if not version.get(row.docname):
					idx = 0
					version[row.docname] = {
						'name':row.docname,
						'creation_date':row.creation,
						'posting_date':row.posting_date,
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':row.owner,
						f'{state_counter[idx]}_approval_on':row.versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.versioncreation - row.creation).days
					}				
				else:
					idx += 1
					version[row.docname].update({
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':row.owner,
						f'{state_counter[idx]}_approval_on':row.versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					})
	columns = get_columns(state_list, state_counter)
	return columns , list(version.values())

def get_columns(state_list, state_counter):
	columns = [
		{
			"label": _("Purchase Invoice"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 180,
		},
		{
			"label": _("Creation Date"),
			"fieldname": "creation_date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150,
		},
	]
	for idx, row in enumerate(state_list):
		columns += [
			{
				"label": _(f"{state_counter[idx]} State"),
				"fieldname": f"{state_counter[idx]}_state",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _(f"{state_counter[idx]} Approver"),
				"fieldname": f"{state_counter[idx]}_approver",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _(f"{state_counter[idx]} Approval On"),
				"fieldname": f"{state_counter[idx]}_approval_on",
				"fieldtype": "Datetime",
				"width": 150,
			},
			{
				"label": _(f"days_to_{state_counter[idx]}_approve"),
				"fieldname": f"days_to_{state_counter[idx]}_approve",
				"fieldtype": "Data",
				"width": 150,
			},
		]
	return columns
