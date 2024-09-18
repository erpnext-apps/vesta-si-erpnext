# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	data, chart = get_data(filters)

	columns = [
		{
			"fieldname" : "workflow_state",
			"label" : "Approval Status",
			"fieldtype" : "Link",
			"options" : "Workflow State",
			"width" :150
		},
		{
			"fieldname" : "name",
			"label" : "Purchase Invoice",
			"fieldtype" : "Link",
			"options" : "Purchase Invoice",
			"width" :200
		},
		{
			"fieldname" : "supplier",
			"label" : "Supplier",
			"fieldtype" : "Link",
			"options" : "Supplier",
			"width" :150
		},
		{
			"fieldname" : "supplier_name",
			"label" : "Supplier Name",
			"fieldtype" : "Data",
			"width" :150
		},
		{
			"fieldname" : "net_amount",
			"label" : "Net Amount",
			"fieldtype" : "Currency",
			"width" :150
		},
		{
			"fieldname" : "amount",
			"label" : "Amount",
			"fieldtype" : "Currency",
			"width" :150
		}
	]
	return columns, data, None, chart



def get_data(filters):
	data = frappe.db.sql("""
		Select pi.name, pi.workflow_state, pi.supplier, pi.supplier_name, pii.net_amount, pii.amount, pii.expense_account, pi.posting_date
		From `tabPurchase Invoice` as pi
		Left Join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
		Where pi.docstatus = 1 and pii.expense_account in ('629301 - Reminder Fee & Penalty Cost (operational) - 9150', '824502 - Interest expense due to late payment - 9150')
	""", as_dict = 1)

	january = []
	february = []
	march = []
	april = []
	may = [] 
	june = []
	july = []
	august = []
	september = []
	october = []
	november = []
	december = []

	january_total_629301, january_total_824502 = 0, 0
	february_total_629301 , february_total_824502  = 0, 0
	march_total_629301, march_total_824502 = 0, 0
	april_total_629301, april_total_824502 = 0, 0
	may_total_629301, may_total_824502 = 0, 0 
	june_total_629301, june_total_824502 = 0, 0
	july_total_629301, july_total_824502,  = 0, 0
	august_total_629301, august_total_824502 = 0, 0
	september_total_629301, september_total_824502 = 0, 0
	october_total_629301, october_total_824502 = 0, 0
	november_total_629301, november_total_824502 = 0, 0
	december_total_629301, december_total_824502 = 0, 0

	for row in data:
		if row.posting_date.month == 1:
			january.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				january_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				january_total_824502 += row.get("net_amount")

		if row.posting_date.month == 2:
			february.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				february_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				february_total_824502 += row.get("net_amount")
		if row.posting_date.month == 3:
			march.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				march_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				march_total_824502 += row.get("net_amount")

		if row.posting_date.month == 4:
			april.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				april_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				april_total_824502 += row.get("net_amount")

		if row.posting_date.month == 5:
			may.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				may_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				may_total_824502 += row.get("net_amount")

		if row.posting_date.month == 6:
			june.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				june_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				june_total_824502 += row.get("net_amount")

		if row.posting_date.month == 7:
			july.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				july_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				july_total_824502 += row.get("net_amount")

		if row.posting_date.month == 8:
			august.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				august_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				august_total_824502 += row.get("net_amount")

		if row.posting_date.month == 9:
			september.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				september_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				september_total_824502 += row.get("net_amount")

		if row.posting_date.month == 10:
			october.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				october_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				october_total_824502 += row.get("net_amount")

		if row.posting_date.month == 11:
			november.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				november_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				november_total_824502 += row.get("net_amount")

		if row.posting_date.month == 12:
			december.append(row)
			if row.expense_account == "629301 - Reminder Fee & Penalty Cost (operational) - 9150":
				december_total_629301 += row.get("net_amount")
			if row.expense_account == "824502 - Interest expense due to late payment - 9150":
				december_total_824502 += row.get("net_amount")
		
	label = [	"january",
				"february",
				"march",
				"april",
				"may",
				"june",
				"july",
				"august",
				"september",
				"october",
				"november",
				"december"]
	value1 = [
		january_total_629301,
		february_total_629301,
		march_total_629301,
		april_total_629301,
		may_total_629301, 
		june_total_629301,
		july_total_629301,
		august_total_629301,
		september_total_629301,
		october_total_629301,
		november_total_629301,
		december_total_629301,
	]
	value2 = [
		january_total_824502,
		february_total_824502,
		march_total_824502,
		april_total_824502,
		may_total_824502, 
		june_total_824502,
		july_total_824502,
		august_total_824502,
		september_total_824502,
		october_total_824502,
		november_total_824502,
		december_total_824502,
	]
	chart = get_chart_data(label, value1, value2)
	return data, chart

def get_chart_data(label , value1, value2):
	return {
			
			"data": {
					'labels': label,
					'datasets': [
						{
							'name': '629301',
							'values': value1,
							'chartType': 'bar',
						},
						{
							'name': '824502',
							'values': value2,
							'chartType': 'bar',
						}
					]
				},
				"type": "line",
			}
