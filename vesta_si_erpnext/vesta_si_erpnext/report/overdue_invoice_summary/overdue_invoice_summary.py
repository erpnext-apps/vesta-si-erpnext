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
	range1 = int(filters.get('range1'))
	range2 = int(filters.get('range2'))
	range3 = int(filters.get('range3'))
	
	labels = []
	labels.append("{}-{}".format(0,range1))
	labels.append("{}-{}".format(range1,range2))
	labels.append("{}-{}".format(range2,range3))
	labels.append("{}-{}".format("After", range3))
	
	chart_value = {}

	for row in data:
		if flt(row.day_diff) <= range1:
			if not chart_value.get('range1'):
				chart_value['range1'] = []
				chart_value['total_range1'] = []
				chart_value['pro_days1'] = []
				chart_value['range1'].append(row.get('day_diff'))
				chart_value['total_range1'].append(row.get('base_grand_total'))
				chart_value['pro_days1'].append(row.get('processing_days'))
			else:
				chart_value['range1'].append(row.get('day_diff'))
				chart_value['total_range1'].append(row.get('base_grand_total'))
				chart_value['pro_days1'].append(row.get('processing_days'))

		if range1 < flt(row.day_diff) <= range2:
			if not chart_value.get('range2'):
				chart_value['range2'] = []
				chart_value['total_range2'] = []
				chart_value['pro_days2'] = []
				chart_value['range2'].append(row.get('day_diff'))
				chart_value['total_range2'].append(row.get('base_grand_total'))
				chart_value['pro_days2'].append(row.get('processing_days'))
			else:
				chart_value['range2'].append(row.get('day_diff'))
				chart_value['total_range2'].append(row.get('base_grand_total'))
				chart_value['pro_days2'].append(row.get('processing_days'))

		if range2 < flt(row.day_diff) <= range3:
			if not chart_value.get('range3'):
				chart_value['range3'] = []
				chart_value['pro_days3'] = []
				chart_value['total_range3'] = []
				chart_value['range3'].append(row.get('day_diff'))
				chart_value['total_range3'].append(row.get('base_grand_total'))
				chart_value['pro_days3'].append(row.get('processing_days'))
			else:
				chart_value['range3'].append(row.get('day_diff'))
				chart_value['total_range3'].append(row.get('base_grand_total'))
				chart_value['pro_days3'].append(row.get('processing_days'))
			
		if range3 < flt(row.day_diff):
			if not chart_value.get('range4'):
				chart_value['range4'] = []
				chart_value['pro_days4'] = []
				chart_value['total_range4'] = []
				chart_value['range4'].append(row.get('day_diff'))
				chart_value['total_range4'].append(row.get('base_grand_total'))
				chart_value['pro_days4'].append(row.get('processing_days'))
			else:
				chart_value['range4'].append(row.get('day_diff'))
				chart_value['total_range4'].append(row.get('base_grand_total'))
				chart_value['pro_days4'].append(row.get('processing_days'))

	row = [
		len(chart_value.get('range1')) if chart_value.get('range1') else 0,
		len(chart_value.get('range2')) if chart_value.get('range2') else 0,
		len(chart_value.get('range3')) if chart_value.get('range3') else 0,
		len(chart_value.get('range4')) if chart_value.get('range4') else 0
	]

	total_value = [
		sum(chart_value.get('total_range1')) if chart_value.get('total_range1') else 0,
		sum(chart_value.get('total_range2')) if chart_value.get('total_range2') else 0,
		sum(chart_value.get('total_range3')) if chart_value.get('total_range3') else 0,
		sum(chart_value.get('total_range4')) if chart_value.get('total_range4') else 0
	]

	pro_total_value = [
		sum(chart_value.get('pro_days1')) if chart_value.get('pro_days1') else 0,
		sum(chart_value.get('pro_days2')) if chart_value.get('pro_days2') else 0,
		sum(chart_value.get('pro_days3')) if chart_value.get('pro_days3') else 0,
		sum(chart_value.get('pro_days4')) if chart_value.get('pro_days4') else 0
	]
	if filters.get('chart_type') == "Pie":
		chart =	{
			"data": {
						'labels': labels,
						'datasets': [
							{
								'name': 'Payment Delayed',
								'values': row,
								'type': 'pie',
								"color": "#blue"
							},
							{
								'name': 'Total',
								'values': total_value if filters.get('chart_base_on') == "Delayed Days" else pro_total_value,
								'type': 'pie',
								"color": "#008000"
							},
							
						]
					},
					'type': 'pie',
					'height': 250,
					"colors": ["#blue","008000"],
				}

	if filters.get('chart_type') == "Line":
		chart =	{
			"data": {
						'labels': labels,
						'datasets': [
							{
								'name': 'Payment Delayed',
								'values': row,
								'type': 'line',
								"color": "#blue"
							},
							{
								'name': 'Total',
								'values': total_value if filters.get('chart_base_on') == "Delayed Days" else pro_total_value ,
								'type': 'line',
								"color": "#008000"
							},
							
						]
					},
					'type': 'line',
					'height': 250,
					"colors": ["#blue","008000"],
				}
	if filters.get('chart_type') == "Bar":
		chart =	{
			"data": {
						'labels': labels,
						'datasets': [
							{
								'name': 'Payment Delayed',
								'values': row,
								'type': 'bar',
								"color": "#blue"
							},
							{
								'name': 'Total',
								'values': total_value if filters.get('chart_base_on') == "Delayed Days" else pro_total_value,
								'type': 'bar',
								"color": "#008000"
							},
							
						]
					},
					'type': 'bar',
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