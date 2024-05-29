# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.utils import getdate
from datetime import datetime


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	column = [
		{
		'fieldname' : 'purchase_invoice',
		'label' : _('Purchase Invoice ID'),
		'fieldtype': 'Link',
		'options' :'Purchase Invoice',
		'width': 120
		},
		{
		'fieldname': 'creation',
		'label': _('Creation Date'),
		'fieldtype': 'Date',
		'width': 100
		},
		{
		'fieldname': 'invoice_date',
		'label': _('Invoice Date'),
		'fieldtype': 'Date',
		'width': 100
		},
		{
		'fieldname': 'due_date',
		'label': _('Due Date'),
		'fieldtype': 'Date',
		},
		{
		'fieldname': 'payment_date',
		'label': _('Payment Date'),
		'fieldtype': 'Date',
		},
		{
		'fieldname': 'day_diff',
		'label': _('Day Diff'),
		'fieldtype': 'Data',
		'width': 100
		},
		{
		'fieldname': 'supplier_name',
		'label' : _('Supplier Name'),
		'filedtype': 'Data',
		'width' : 150
		},
		{
		'fieldname': 'status',
		'label': _('Status'),
		'fieldtype': 'Data',
		'width': 200
		},
		{
		'fieldname': 'supplier',
		'label': _('Supplier'),
		'fieldtype':'Link',
		'options': 'Supplier',
		'width': 250
		},
		{
		'fieldname': 'workflow_state',
		'label': _('Approval Status'),
		'fieldtype': 'Link',
		'options': 'Workflow State',
		'width': 200
		},
		{
		'fieldname': 'company',
		'label': _('Company'),
		'fieldtype': 'Link',
		'options': 'Company',
		'width': 200
		},
		{
		'fieldname': 'cost_center',
		'label' : _('Cost Center'),
		'fieldtype': 'Link',
		'options': 'Cost Center',
		'width': 100
		}
	]
	return column


def get_data(filters):
	cond = ''
	if filters.get('from_date'):
		cond += f" and pi.posting_date >= '{filters.get('from_date')}'"
	if filters.get('to_date'):
		cond += f" and pi.posting_date <= '{filters.get('to_date')}'"

	query = f'''

	SELECT 
	pi.name as purchase_invoice, 
	pi.creation, 
	pi.posting_date as invoice_date,
	pi.supplier_name, pi.status, 
	pi.supplier, pi.due_date, 
	pi.workflow_state, 
	pi.company, 
	pi.cost_center, 
	per.parent as payment_entry,
	pe.posting_date as payment_date 
	FROM `tabPurchase Invoice` as pi
	LEFT JOIN `tabPayment Entry Reference` as per ON pi.name = per.reference_name 
	left join `tabPayment Entry` as pe ON per.parent = pe.name
	WHERE pi.docstatus=1 {cond} ORDER BY pi.posting_date 
	
	'''

	query = f'''{query}'''
				
	result = frappe.db.sql(f"{query}", as_dict=True)
	
	result_map = {}

	for row in result:
		result_map[row.payment_entry] = row

	version_data = get_version_data()
	data = []
	for row in version_data:
		if result_map.get(row.get('payment_entry')):
			date_format = "%Y-%m-%d"
			creation = datetime.strptime(str(getdate(row.get('creation'))), date_format)
			payment_date = datetime.strptime(str(result_map.get(row.get('payment_entry')).get('due_date')), date_format)
			result_map.get(row.get('payment_entry')).update({'day_diff': (creation - payment_date).days, 'payment_date':row.get('creation')})
			data.append(result_map.get(row.get('payment_entry')))
	

	return data

def get_version_data():
	data = frappe.db.sql(f"""
		Select name, docname, data, creation
		From `tabVersion`
		where ref_doctype = "Payment Entry"
	""",as_dict=1)

	version_data = []

	for row in data:
		data = json.loads(row.data)
		for d in data.get('changed'):
			if d[0] == "status" and d[1] == "Draft" and d[2] == "Submitted":
				version_data.append({'payment_entry' : row.docname , 'creation' : row.creation})

	return version_data