# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.utils import flt


def execute(filters=None):
	columns, data = [], []
	data = get_purchase_data(filters)
	columns = get_columns(filters)
	return columns, data


def get_purchase_data(filters):
	cond = ''
	if filters.get("from_date"):
		cond += f" and pi.posting_date >= '{filters.get('from_date')}'"
	if filters.get("to_date"):
		cond += f" and pi.posting_date <= '{filters.get('to_date')}'"

	data = frappe.db.sql(f"""
				Select po.name as purchase_order, pi.conversion_rate as pi_conversion_rate, pi.currency, pi.grand_total, 
				po.transaction_date as po_date, pi.posting_date as pi_date, pi.name as purchase_invoice,pi.base_grand_total,
				po.conversion_rate as po_exchange_rate 
				From `tabPurchase Order` as po
				Left Join `tabPurchase Invoice Item` as pii ON pii.purchase_order = po.name
				Left Join `tabPurchase Invoice` as pi ON pi.name = pii.parent
				where po.docstatus = 1 and po.currency != 'SEK' and pi.docstatus = 1 and pi.paid {cond}
				Group By pi.name
			""", as_dict = 1)
	pi_data = frappe.db.sql(f"""
				Select pe.name as payment_entry, paid_from_account_currency, per.reference_name, per.reference_doctype, pe.source_exchange_rate as pe_exchange_rate,
				per.allocated_amount, ped.amount, ped.account
				From `tabPayment Entry` as pe
				Left Join `tabPayment Entry Reference` as per ON per.parent = pe.name
				Left Join  `tabPayment Entry Deduction` as ped ON ped.parent = pe.name
				Where pe.docstatus = 1 and pe.payment_type = 'Pay' and per.reference_doctype = 'Purchase Invoice' and pe.paid_to_account_currency != 'SEK'
	""", as_dict=1)
	
	pi_map_data = {}
	for row in pi_data:
		pi_map_data[row.reference_name] = row

	for row in data:
		base_currency = row.currency
		target_currency = "SEK"
		date=row.pi_date
		exch_data = fetch_exchange_rate(base_currency, target_currency, date)
		row.update({"exchange_rate_on_posting" : exch_data.get("rates").get("SEK"), "different_in_exchange_rate" :flt(row.pi_conversion_rate) - flt(exch_data.get("rates").get("SEK")) })
		if pi_map_data.get(row.purchase_invoice):
			row.update(pi_map_data.get(row.purchase_invoice))
	
	return data

def get_columns(filters):
	columns = [
		{
			"fieldname" : "purchase_order",
			"fieldtype" : "Link",
			"label" : "Purchase Order",
			"options" : "Purchase Order",
			"width" : 150
		},
		{
			"fieldname" : "po_exchange_rate",
			"fieldtype" : "Float",
			"label" : "PO Exchange Rate",
			"width" : 150
		},
		{
			"fieldname" : "currency",
			"fieldtype" : "Link",
			"label" : "Currency",
			"options" : "Currency",
			"width" : 150
		},
		{
			"fieldname" : "purchase_invoice",
			"fieldtype" : "Link",
			"label" : "Purchase Invoice",
			"options" : "Purchase Invoice",
			"width" : 150
		},
		{
			"fieldname" : "pi_date",
			"fieldtype" : "date",
			"label" : "PI Date",
			"options" : "Purchase Invoice",
			"width" : 150
		},
		{
			"fieldname" : "pi_conversion_rate",
			"fieldtype" : "Float",
			"label" : "PI Exchange Rate",
			"width" : 150
		},
		{
			"fieldname" : "exchange_rate_on_posting",
			"fieldtype" : "Float",
			"label" : "PI Exchange Rate(Posting Date)",
			"width" : 200
		},
		{
			"fieldname" : "different_in_exchange_rate",
			"fieldtype" : "Float",
			"label" : "Different in Exchange Rate",
			"width" : 200
		},
		{
			"fieldname" : "grand_total",
			"fieldtype" : "Currency",
			"label" : "PI Total Amount",
			"options": "currency",
			"width" : 150
		},
		{
			"fieldname" : "base_grand_total",
			"fieldtype" : "Currency",
			"label" : "PI Total Amount(SEK)",
			"width" : 150
		},
		{
			"fieldname" : "pe_exchange_rate",
			"fieldtype" : "Float",
			"label" : "PE Exchange Rate",
			"width" : 150
		},
		{
			"fieldname" : "allocated_amount",
			"fieldtype" : "Currency",
			"label" : "PE Allocated Amount",
			"options": "currency",
			"width" : 150
		},
		{
			"fieldname" : "payment_entry",
			"fieldtype" : "Link",
			"label" : "Payment Entry",
			"options" : "Payment Entry",
			"width" : 150	
		},
		{
			"fieldname" : "amount",
			"fieldtype" : "Currency",
			"label" : "Payment Deductions or Loss",
			"width" : 150
		},
		{
			"fieldname" : "account",
			"fieldtype" : "Link",
			"label" : "Exchange Gain or Loss Account",
			"options" : "Account",
			"width" : 150
		}
		
	]
	return columns

def fetch_exchange_rate(base_currency, target_currency, date):
    url = f"https://api.frankfurter.app/{date}"
    params = {
        'base': base_currency,
        'symbols': target_currency
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return {
            'date': data.get('date'),
            'base': data.get('base'),
            'rates': data.get('rates')
        }
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

	

	
	
