# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from vesta_si_erpnext.vesta_si_erpnext.report.unhappy_po_timeline_report.unhappy_po_timeline_report import execute as unhappy_po_timeline, get_columns
import json
from frappe import _
from datetime import date
from frappe.utils import getdate, flt

def execute(filters=None):
	columns, data = [], []
	columns_pi , pi_timeline = get_purchase_invoice_timeline_report(filters)
	po_timeline = unhappy_po_timeline_report(filters)

	pi_timeline_map = {}

	for row in pi_timeline:
		if row.get('pi_purchase_order'):
			pi_timeline_map[row.get('pi_purchase_order')] = row

	for row in po_timeline:
		if pi_timeline_map.get(row.get('purchase_order')):
			row.update(pi_timeline_map.get(row.get('purchase_order')))

	uptr_columns = get_columns(filters)
	columns = uptr_columns + columns_pi

	return columns, po_timeline

def get_purchase_invoice_timeline_report(filters):
	workflow = frappe.get_doc('Workflow', {'document_type' : "Purchase Invoice" , 'is_active':1})
	workflow_creation = workflow.creation
	condition = ''
	if filters.get("workflow_state"):
		condition = f" and po.workflow_state = '{filters.get('workflow_state')}'"

	query = frappe.db.sql(f""" 
		Select v.data,
		po.name as purchase_invoice, 
		po.creation as pi_creation, 
		po.posting_date as pi_posting_date, 
		v.owner as pi_owner, 
		v.creation as pi_versioncreation, 
		v.docname,
		po.bill_date,
		per.parent as payment_entry
		from `tabPurchase Invoice` as po 
		left join `tabVersion` as v on po.name = v.docname
		Left Join `tabPayment Entry Reference` as per ON per.reference_doctype = "Purchase Invoice" and per.reference_name = po.name
		where data like '%workflow_state%' and ref_doctype = 'Purchase Invoice' and po.creation > '2024-01-01 00:00:00' {condition}
		order by docname , v.creation
	""",as_dict = 1)

	poi_data = frappe.db.sql(f"""
			Select purchase_order, sum(net_amount), parent
			From `tabPurchase Invoice Item`
			where docstatus != 2
			Group By purchase_order
	""", as_dict= 1)
	
	poi_data_map = {}
	for row in poi_data:
		poi_data_map[row.parent] = row
	
	for row in query:
		if poi_data_map.get(row.purchase_invoice):
			row.update({'purchase_order': poi_data_map.get(row.purchase_invoice).get('purchase_order')})

	data = query
	

	log = []

	
	workstate_list = []
	for row in workflow.transitions:
		workstate_list.append(row.next_state)
		if row.next_state == "Approved":
			break

	version = {}
	state_counter = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh']

	days_to_First_approve = 0 
	days_to_Second_approve = 0 
	days_to_Third_approve = 0 
	days_to_Fourth_approve = 0 
	days_to_Fifth_approve = 0 
	days_to_Sixth_approve = 0 
	days_to_Seventh_approve = 0 
	days_to_Eighth_approve = 0 
	days_to_Ninth_approve = 0 
	days_to_Tenth_approve = 0

	average_processing_days = 0 
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
						'pi_name':row.docname,
						"payment_entry":row.payment_entry,
						'pi_creation_date':row.pi_creation,
						'bill_date':row.bill_date,
						'pi_posting_date':row.pi_posting_date,
						'pi_purchase_order':row.purchase_order,
						'pi_processing_days':(row.pi_posting_date - getdate(row.pi_creation)).days,
						'pi_proce_days':(getdate(row.pi_creation) - row.bill_date).days if row.bill_date else 0,
						'pi_proce_days_posting':(row.pi_posting_date - row.bill_date).days if row.bill_date else 0,
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':frappe.db.get_value("User", row.pi_owner, "full_name"),
						f'{state_counter[idx]}_approval_on':row.pi_versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.pi_versioncreation - row.pi_creation).days,
					}
					days_to_First_approve += (row.pi_versioncreation - row.pi_creation).days
					average_processing_days += flt((row.pi_posting_date - getdate(row.pi_creation)).days)				
				else:
					idx += 1
					version[row.docname].update({
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':frappe.db.get_value("User", row.pi_owner, "full_name"),
						f'{state_counter[idx]}_approval_on':row.pi_versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.pi_versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					})
					
	data = list(version.values())
	columns = get_columns_pi(state_list, state_counter)
	return columns , data

def unhappy_po_timeline_report(filters):
	data = get_version_data(filters)
	return data

def get_version_data(filters):

	conditions = ''
	if filters.get("from_date"):
		conditions += f" and po.transaction_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.transaction_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name, po.creation, po.transaction_date, v.owner, v.creation as versioncreation, po.owner, per.parent as payment_entry
		from `tabPurchase Order` as po 
		left join `tabVersion` as v on po.name = v.docname
		Left Join `tabPayment Entry Reference` as per ON per.reference_doctype = "Purchase Order" and per.reference_name = po.name
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
					"payment_entry":row.payment_entry,
					'creation':row.creation,
					'posting_date':row.transaction_date,
					'approval_user':row.owner,
					"versioncreation":row.versioncreation,
					"days": (row.versioncreation - row.creation).days,
					"processing_days": (getdate(row.creation) - row.transaction_date).days,
					'created_by' : frappe.db.get_value("User", row.owner, 'full_name')
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

	
	return log

def get_columns_pi(state_list, state_counter):
	columns = [
		{
			"label": _("Purchase Invoice"),
			"fieldname": "pi_name",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 180,
		},
		{
			"label": _("Payment Entry"),
			"fieldname": "payment_entry",
			"fieldtype": "Link",
			"options": "Payment Entry",
			"width": 180,
		},
		{
			"label": _(" PI Creation Date"),
			"fieldname": "pi_creation_date",
			"fieldtype": "Datetime",
			"width": 180,
		},
		{
			"label": _("Supplier Invoice Date"),
			"fieldname": "bill_date",
			"fieldtype": "Date",
			"width": 180,
		},
		{
			"label": _("Delay In PI Creation"),
			"fieldname": "pi_proce_days",
			"fieldtype": "Data",
			"width": 180,
		},
		
		{
			"label": _("PI Posting Date"),
			"fieldname": "pi_posting_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Delay In PI Posting"),
			"fieldname": "pi_proce_days_posting",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("PI Processing Days"),
			"fieldname": "pi_processing_days",
			"fieldtype": "Data",
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
				"label": _(f"Days to {state_counter[idx]} Approve"),
				"fieldname": f"days_to_{state_counter[idx]}_approve",
				"fieldtype": "Data",
				"width": 150,
			},
		]
	
	return columns

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_workflow_state(doctype, txt, searchfield, start=0, page_len=20, filters=None):
	document = filters.get('docname')
	workflow = frappe.db.sql("""""")
	data = frappe.db.sql(f"""
			Select state
			From `tabWorkflow Document State`
			Where parent = '{workflow}'
	""")
	return data