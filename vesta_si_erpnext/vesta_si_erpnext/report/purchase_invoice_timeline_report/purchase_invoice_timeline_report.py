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
		conditions += f" and po.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.posting_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name as purchase_invoice, po.creation, po.posting_date, v.owner, v.creation as versioncreation, v.docname
		from `tabPurchase Invoice` as po 
		left join `tabVersion` as v on po.name = v.docname
		where data like '%workflow_state%' and ref_doctype = 'Purchase Invoice' {conditions}
		order by docname
	""",as_dict = 1)
	log = []
	workflow = frappe.get_doc('Workflow', {'document_type' : "Purchase Invoice" , 'is_active':1})
	state_list = []
	for row in workflow.transitions:
		if row.action == "Approve":
			state_list.append(row.state)
	version = {}
	for row in data:
		d = json.loads(row.data)
		for r in d.get('changed'):
			if not r[0] == 'workflow_state':
				continue
			if r[0] == 'workflow_state' and r[-1] == "Submitted to Chief Accountant":
				if not version.get(row.purchase_invoice):
					version[row.purchase_invoice] = {
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'submition_state' : r[-1],
						'name_of_chief' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'first_submission_date' : row.versioncreation,
						'days_to_submit' : (row.versioncreation - row.creation).days
					}
				else:
					version[row.purchase_invoice].update({
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'submition_state' : r[-1],
						'name_of_chief' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'first_submission_date' : row.versioncreation,
						'days_to_submit' : (row.versioncreation - row.creation).days
					})
			if r[0] == 'workflow_state' and r[-1]  == "Approved by Chief Accountant":
				if not version.get(row.purchase_invoice):
					version[row.purchase_invoice] = {
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'first_approve_state' : r[-1],
						'first_chief_accountant' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'first_chief_accountant_approval_date' : row.versioncreation,
						'days_to_approve_by_first_chief' : (row.versioncreation - row.creation).days
					}
				else:
					version[row.purchase_invoice].update({
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'first_approve_state' : r[-1],
						'first_chief_accountant' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'first_chief_accountant_approval_date' : row.versioncreation,
						'days_to_approve_by_first_chief' : (row.versioncreation - row.creation).days
					})
			if r[0] == 'workflow_state' and r[-1] in state_list:
				if not version.get(row.purchase_invoice):
					version[row.purchase_invoice] = {
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'approve_state' : r[-1],
						'chief_accountant' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'chief_accountant_approval_date' : row.versioncreation,
						'days_to_approve_by_chief' : (row.versioncreation - row.creation).days
					}
				else:
					version[row.purchase_invoice].update({
						'purchase_invoice': row.purchase_invoice,
						'creation' : row.creation,
						'posting_date' : row.posting_date,
						'approve_state' : r[-1],
						'chief_accountant' : frappe.db.get_value('User' , row.owner , 'full_name'),
						'chief_accountant_approval_date' : row.versioncreation,
						'days_to_approve_by_chief' : (row.versioncreation - row.creation).days
					})
					
					
			if r[0] == 'workflow_state' and r[-1] == 'Approved':
				if not version.get(row.purchase_invoice):
					version[row.purchase_invoice] = {
						'final_state': 'Approved',
						'approval_user':frappe.db.get_value('User' , row.owner , 'full_name'),
						"approved_date":row.versioncreation,
						"days_to_approved": (row.versioncreation - row.creation).days
					}
				else:
					version[row.purchase_invoice].update({
						'final_state': 'Approved',
						'approval_user':frappe.db.get_value('User' , row.owner , 'full_name'),
						"approved_date":row.versioncreation,
						"days_to_approved": (row.versioncreation - row.creation).days
					})
	data = list(version.values())
	for row in data:
		if row.get('days_to_approved'):
			row.update({'days_to_approved': (row.get('approved_date') - row.get('chief_accountant_approval_date')).days})
		if row.get('days_to_approve_by_chief'):
			row.update({'days_to_approve_by_chief': (row.get('chief_accountant_approval_date') - row.get('first_chief_accountant_approval_date')).days})
		if row.get('days_to_approve_by_first_chief'):
			row.update({'days_to_approve_by_first_chief': (row.get('first_chief_accountant_approval_date') - row.get('first_submission_date')).days}) 


	return data


def get_columns(filters):
	columns = [
		{
			"label": _("Purchase Invoice"),
			"fieldname": "purchase_invoice",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
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
			"label": _("First Submission State"),
			"fieldname": "submition_state",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Chief Accountant"),
			"fieldname": "name_of_chief",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Submission date"),
			"fieldname": "first_submission_date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Days to Submit"),
			"fieldname": "days_to_submit",
			"fieldtype": "Data",
			"width": 100,
		},
		

		{
			"label": _("First Approval State"),
			"fieldname": "first_approve_state",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("R2R Chief Accountant"),
			"fieldname": "first_chief_accountant",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("First Approved date"),
			"fieldname": "first_chief_accountant_approval_date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Days to First Approval"),
			"fieldname": "days_to_approve_by_first_chief",
			"fieldtype": "Data",
			"width": 100,
		},


		{
			"label": _("Second Approval State"),
			"fieldname": "approve_state",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Chief Accountant"),
			"fieldname": "chief_accountant",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Approved date"),
			"fieldname": "chief_accountant_approval_date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Days to Second Approval"),
			"fieldname": "days_to_approve_by_chief",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("State"),
			"fieldname": "final_state",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Final Approver"),
			"fieldname": "approval_user",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Approved Date"),
			"fieldname": "approved_date",
			"fieldtype": "Datetime",
			"width": 100,
		},
		{
			"label": _("Days To Final Approval"),
			"fieldname": "days_to_approved",
			"fieldtype": "Data",
			"width": 100,
		}
	]
	return columns