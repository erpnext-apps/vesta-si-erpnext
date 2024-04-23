# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []

	data = frappe.db.sql(f"""
			Select pi.name as purchase_receipt,pi.posting_date, pii.purchase_order, sum(pii.base_amount) as total
			From `tabPurchase Receipt` as pi
			Left join `tabPurchase Receipt Item` as pii ON pi.name = pii.parent
			where pi.docstatus = 1 and pii.expense_account = "222501 - Goods & services received/Invoice received - non SKF - 9150" and
			(pii.purchase_invoice = '' or pii.purchase_invoice is null) 
			Group By pi.name
	""", as_dict = 1)
	
	po_data = frappe.db.sql(f"""
			Select po.name, pri.parent as purchase_invoice
			From `tabPurchase Order` as po
			Left Join `tabPurchase Invoice Item` as pri ON po.name = pri.purchase_order 
			Where po.docstatus = 1
	""", as_dict = 1)


	pi_data = frappe.db.sql(f"""
		Select pi.name , pii.purchase_receipt
		From `tabPurchase Invoice` as pi
		Left join `tabPurchase Invoice Item` as pii on pii.parent = pi.name
		Where pi.docstatus = 1
	""",as_dict=1)

	pr_data_map = {}
	for row in po_data:
		if row.purchase_invoice:
			pr_data_map[row.name] = row

	filtered_data = []
	for row in data:
		if not row.purchase_order:
			filtered_data.append(row)
		if not pr_data_map.get(row.purchase_order):
			filtered_data.append(row)
	
	pi_data_map = {}
	for row in pi_data:
		pi_data_map[row.purchase_receipt] = row

	data = []
	for row in filtered_data:
		if not pi_data_map.get(row.purchase_receipt):
			data.append(row)
	
	pr = []
	f_data = []
	for row in data:
		if row.purchase_receipt not in pr:
			pr.append(row.purchase_receipt)
			f_data.append(row)

	data = f_data

	columns = [
		{
			'fieldname': 'purchase_receipt',
			'fieldtype': 'Link',
			'label': 'Purchase Receipt',
			'options': 'Purchase Receipt',
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
