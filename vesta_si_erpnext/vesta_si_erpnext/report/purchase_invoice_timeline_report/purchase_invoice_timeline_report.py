# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from datetime import date
from frappe.utils import getdate, flt


def execute(filters=None):
	columns, data = [], []
	columns , data , chart = get_version_data(filters)
	return columns, data , None , chart


def get_version_data(filters):

	conditions = ''
	if filters.get("from_date"):
		conditions += f" and po.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		conditions += f" and po.posting_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f""" 
		Select v.data, po.name as purchase_invoice, po.creation, po.posting_date, v.owner, v.creation as versioncreation , v.docname, po.bill_date
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
						'name':row.docname,
						'creation_date':row.creation,
						'bill_date':row.bill_date,
						'posting_date':row.posting_date,
						'processing_days':(row.posting_date - getdate(row.creation)).days,
						'proce_days':(getdate(row.creation) - row.bill_date).days if row.bill_date else 0,
						'proce_days_posting':(row.posting_date - row.bill_date).days if row.bill_date else 0,
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':frappe.db.get_value("User", row.owner, "full_name"),
						f'{state_counter[idx]}_approval_on':row.versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.versioncreation - row.creation).days,
					}
					days_to_First_approve += (row.versioncreation - row.creation).days
					average_processing_days += flt((row.posting_date - getdate(row.creation)).days)				
				else:
					idx += 1
					version[row.docname].update({
						f'{state_counter[idx]}_state':r[-1],
						f'{state_counter[idx]}_approver':frappe.db.get_value("User", row.owner, "full_name"),
						f'{state_counter[idx]}_approval_on':row.versioncreation,
						f'days_to_{state_counter[idx]}_approve':(row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					})
					if idx == 1:
						days_to_Second_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 2:
						days_to_Third_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 3:
						days_to_Fourth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 4:
						days_to_Fifth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 5:
						days_to_Sixth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 6:
						days_to_Seventh_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 7:
						days_to_Eighth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days
					if idx == 8:
						days_to_Ninth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days	
					if idx == 9:
						days_to_Tenth_approve += (row.versioncreation - version[row.docname].get(f'{state_counter[idx-1]}_approval_on')).days

	data = list(version.values())

	# chart  = prepare_chart_data(data)

	average_row = {
			"processing_days": "<b>Average : {0}</b>".format(round(average_processing_days/len(data),2)),
			"days_to_First_approve": "<b>Average : {0}</b>".format(round(days_to_First_approve/len(data))),
			"days_to_Second_approve": "<b>Average : {0}</b>".format(round(days_to_Second_approve/len(data))),
			"days_to_Fourth_approve": "<b>Average : {0}</b>".format(round(days_to_Fourth_approve/len(data))),
			"days_to_Third_approve": "<b>Average : {0}</b>".format(round(days_to_Third_approve/len(data))),
			"days_to_Fifth_approve": "<b>Average : {0}</b>".format(round(days_to_Fifth_approve/len(data))),
			"days_to_Sixth_approve": "<b>Average : {0}</b>".format(round(days_to_Sixth_approve/len(data))),
			"days_to_Seventh_approve": "<b>Average : {0}</b>".format(round(days_to_Seventh_approve/len(data))),
			"days_to_Eighth_approve": "<b>Average : {0}</b>".format(round(days_to_Eighth_approve/len(data))),
			"days_to_Ninth_approve": "<b>Average : {0}</b>".format(round(days_to_Ninth_approve/len(data))),
			"days_to_Tenth_approve": "<b>Average : {0}</b>".format(round(days_to_Tenth_approve/len(data))),
	}
	
	
	columns = get_columns(state_list, state_counter)
	
	january_row = []
	february_row = []
	march_row = []
	april_row = []
	may_row = [] 
	june_row = []
	july_row = []
	august_row = []
	september_row = []
	october_row = []
	november_row = []
	december_row = []

	january = 0
	february = 0
	march = 0
	april = 0
	may = 0 
	june = 0
	july = 0
	august = 0
	september = 0
	october = 0
	november = 0
	december = 0

	for row in data:
		frappe.msgprint(str(row))
		if getdate(row.get('creation_date')).month == 1:
			january_row.append(row)
			january += flt(row.get('proce_days')) or 0
			continue
		if getdate(row.get('creation_date')).month == 2:
			february_row.append(row)
			february += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 3:
			march_row.append(row)
			march += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 4:
			april_row.append(row)
			april += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 5:
			may_row.append(row)
			may += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 6:
			june_row.append(row)
			june += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 7:
			july_row.append(row)
			july += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 8:
			august_row.append(row)
			august += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 9:
			september_row.append(row)
			september += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 10:
			october_row.append(row)
			october += row.get('proce_days') or 0
		if getdate(row.get('creation_date')).month == 11:
			november_row.append(row)
			november += row.get('proce_days') or 0
			continue
		if getdate(row.get('creation_date')).month == 12:
			december_row.append(row)
			december += row.get('proce_days') or 0
			continue

	label = [
		"january",
		"february",
		"march",
		"april",
		"may" ,
		"june",
		"july",
		"august",
		"september",
		"october",
		"november",
		"december"
	]
	value1 = [
		len(january_row),
		len(february_row),
		len(march_row),
		len(april_row),
		len(may_row) ,
		len(june_row),
		len(july_row),
		len(august_row),
		len(september_row),
		len(october_row),
		len(november_row),
		len(december_row)
	]

	value2 = [
		january_row,
		february_row,
		march_row,
		april_row,
		may_row,
		june_row,
		july_row,
		august_row,
		september_row,
		october_row,
		november_row,
		december_row
	]

	chart = get_chart_data(label, value1, value2)
	return columns , data , chart

def get_chart_data(label , value1, value2):
	return {
			
			"data": {
					'labels': label,
					'datasets': [
						{
							'name': 'Month wise number of delay invoices',
							'values': value1,
							'chartType': 'bar',
						},
						{
							'name': 'Month wise total delay days',
							'values': value2,
							'chartType': 'bar',
						}
					]
				},
				"type": "bar",
			}
	
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
			"label": _("Supplier Invoice Date"),
			"fieldname": "bill_date",
			"fieldtype": "Date",
			"width": 180,
		},
		{
			"label": _("Delay In Invoice Creation"),
			"fieldname": "proce_days",
			"fieldtype": "Data",
			"width": 180,
		},
		
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Delay In Invoice Posting"),
			"fieldname": "proce_days_posting",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Processing Days"),
			"fieldname": "processing_days",
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

