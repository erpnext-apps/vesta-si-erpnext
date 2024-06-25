# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe import _
from frappe.utils import getdate, flt
from datetime import datetime, timedelta	


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data, chart = get_data(filters)
	return columns, data , None, chart

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
		'label': _('Posting Date'),
		'fieldtype': 'Date',
		'width': 100
		},
		{
			"label": _("Processing Days"),
			"fieldname": "processing_days",
			"fieldtype": "Data",
			"width": 150,
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
		'width': 150
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
	pi.base_grand_total,
	pi.cost_center, 
	per.parent as payment_entry,
	pe.posting_date as payment_date 
	FROM `tabPurchase Invoice` as pi
	LEFT JOIN `tabPayment Entry Reference` as per ON pi.name = per.reference_name 
	left join `tabPayment Entry` as pe ON per.parent = pe.name
	WHERE pi.docstatus=1 and pi.status = 'Paid' {cond} ORDER BY pi.posting_date 
	
	'''

	query = f'''{query}'''
				
	result = frappe.db.sql(f"{query}", as_dict=True)
	
	result_map = {}
	total_processing_days  = 0
	for row in result:
		row.update({"processing_days": (row.invoice_date - getdate(row.creation)).days})
		result_map[row.payment_entry] = row
		total_processing_days += (row.invoice_date - getdate(row.creation)).days

	version_data = get_version_data()
	total_days = 0
	data = []
	for row in version_data:
		if result_map.get(row.get('payment_entry')):
			date_format = "%Y-%m-%d"
			creation = datetime.strptime(str(getdate(row.get('creation'))), date_format)
			payment_date = datetime.strptime(str(result_map.get(row.get('payment_entry')).get('due_date')), date_format)
			result_map.get(row.get('payment_entry')).update({'day_diff': (creation - payment_date).days, 'payment_date':row.get('creation')})
			data.append(result_map.get(row.get('payment_entry')))
			total_days += (creation - payment_date).days
	
	total_tow = len(data)
	chart = prepare_chart_data(filters, data)
	data.insert(0,{"day_diff" : "<b>Average : {0}</b>".format(round(total_days/total_tow, 2)), "processing_days":"<b>Average : {0}</b>".format(round(total_processing_days/total_tow, 2))})

	return data, chart

def prepare_chart_data(filters, data):
	range1 = filters.get('range1')
	range2 = int(filters.get('range2')) + int(filters.get('range1'))
	range3 = int(filters.get('range3')) + int(filters.get('range2')) + int(filters.get('range1'))
	current_date = getdate()
	range1_days_to_add = timedelta(days=flt(-range1))
	range1_date = current_date + range1_days_to_add
	range2_days_to_add = timedelta(days=flt(-range2))
	range2_date = current_date + range2_days_to_add
	range3_days_to_add = timedelta(days=flt(-range3))
	range3_date = current_date + range3_days_to_add

	labels = []
	labels.append("{}-{}".format(0,range1))
	labels.append("{}-{}".format(range1,range2))
	labels.append("{}-{}".format(range2,range3))
	labels.append("{}-{}".format("Before", range3))
	
	chart_value = {}

	for row in data:
		if current_date >= row.due_date >= range1_date:
			if not chart_value.get('first'):
				chart_value['first'] = []
				chart_value['first_total'] = []
				chart_value['first'].append(row)
				chart_value['first_total'].append(row.base_grand_total)
			else:
				chart_value['first'].append(row)
				chart_value['first_total'].append(row.base_grand_total)

		if range1_date >= row.due_date >= range2_date:
			if not chart_value.get('second'):
				chart_value['second'] = []
				chart_value['second_total'] = []
				chart_value['second'].append(row)
				chart_value['second_total'].append(row.base_grand_total)
			else:
				chart_value['second'].append(row)
				chart_value['second_total'].append(row.base_grand_total)
			
		if range2_date >= row.due_date >= range3_date:
			if not chart_value.get('third'):
				chart_value['third'] = []
				chart_value['third_total'] = []
				chart_value['third'].append(row)
				chart_value['third_total'].append(row.base_grand_total)
			else:
				chart_value['third'].append(row)
				chart_value['third_total'].append(row.base_grand_total)

		if range3_date >= row.due_date:
			if not chart_value.get('forth'):
				chart_value['forth'] = []
				chart_value['forth_total'] = []
				chart_value['forth'].append(row)
				chart_value['forth_total'].append(row.base_grand_total)
			else:
				chart_value['forth'].append(row)
				chart_value['forth_total'].append(row.base_grand_total)

	row = [
		len(chart_value.get('first')) if chart_value.get('first') else 0,
		len(chart_value.get('second')) if chart_value.get('second') else 0, 
		len(chart_value.get('third')) if chart_value.get('third') else 0, 
		len(chart_value.get('forth')) if chart_value.get('forth') else 0
		]
	total_value = [
		sum(chart_value.get('first_total')) if chart_value.get('first_total') else 0,
		sum(chart_value.get('second_total')) if chart_value.get('second_total') else 0, 
		sum(chart_value.get('third_total')) if chart_value.get('third_total') else 0, 
		sum(chart_value.get('forth_total')) if chart_value.get('forth_total') else 0
		]
	chart =	{
		"data": {
					'labels': labels,
					'datasets': [
						{
							'name': 'Invoice',
							'values': row,
							'type': 'bar',
							"color": "#blue"
						},
						{
							'name': 'Total',
							'values': total_value,
							'type': 'line',
							"color": "#008000"
						},
						
					]
				},
				'type': 'line',
    			'height': 250,
				"colors": ["#blue","008000"],
			}
	
	return chart

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