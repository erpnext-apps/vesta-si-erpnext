# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	# cond = ''
	# if filters.get('from_date'):
	# 	cond = f" and pi.posting_date >= '{filters.get('from_date')}'"

	data = frappe.db.sql(f"""
			Select pi.name as purchase_invoice,pi.posting_date, pii.purchase_order, sum(pii.base_amount) as total
			From `tabPurchase Invoice` as pi
			Left join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
			where pi.docstatus = 1 and pii.expense_account = "222501 - Goods & services received/Invoice received - non SKF - 9150" and
			(pii.purchase_receipt = '' or pii.purchase_receipt is null) 
			Group By pi.name
	""", as_dict = 1)

	po_data = frappe.db.sql(f"""
			Select po.name, pri.parent as purchase_receipt
			From `tabPurchase Order` as po
			Left Join `tabPurchase Receipt Item` as pri ON po.name = pri.purchase_order 
			Where po.docstatus = 1 
	""", as_dict = 1)
	
	pr_data = frappe.db.sql(f"""
		Select pr.name , pri.purchase_invoice  
		From `tabPurchase Receipt` as pr
		Left join `tabPurchase Receipt Item` as pri on pri.parent = pr.name
		Where pr.docstatus = 1
	""",as_dict=1)
	
	po_data_map = {}
	for row in po_data:
		po_data_map[row.name] = row

	filtered_data = []
	for row in data:
		if not row.purchase_order:
			filtered_data.append(row)
			continue
		if po_data_map.get(row.purchase_order):
			if not po_data_map[row.purchase_order].get('purchase_receipt'):
				filtered_data.append(row)
	
	pr_data_map = {}
	for row in pr_data:
		pr_data_map[row.purchase_invoice] = row

	data = []
	for row in filtered_data:
		if not pr_data_map.get(row.purchase_invoice):
			data.append(row)
	
	pi = []
	f_data = []
	for row in data:
		if row.purchase_invoice not in pi:
			pi.append(row.purchase_invoice)
			f_data.append(row)


	data = f_data
	columns = [
		{
			'fieldname': 'purchase_invoice',
			'fieldtype': 'Link',
			'label': 'Purchase Invoice',
			'options': 'Purchase Invoice',
			'width':150
		},
		{
			'fieldname': 'posting_date',
			'fieldtype': 'Date',
			'label': 'Posting Date',
			'width':150
		},
		{
			'fieldname': 'purchase_order',
			'fieldtype': 'Link',
			'label': 'Purchase Order',
			'options': 'Purchase Order',
			'width':150
		},
		{
			'fieldname': 'total',
			'fieldtype': 'Currency',
			'label': 'Total',
			'width':150
		}
		
	]

	
	return columns, data
