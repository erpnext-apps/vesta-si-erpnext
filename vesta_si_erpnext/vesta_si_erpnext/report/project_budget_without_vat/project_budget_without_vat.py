# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	condition = ''
	if filters.get("project"): 
		condition += f" and pro.name = '{filters.get('project')}'"
	
	if filters.get("status"):
		condition += f" and p.status = '{filters.get('status')}'"

	pi_data = frappe.db.sql(f"""
			Select pro.name, 
			pro.project_name, 
			pro.estimated_costing, 
			pro.total_purchase_cost, 
			pro.percent_complete,
			sum(pi.base_net_amount) as pi_net_total
			From `tabProject` as pro
			left join `tabPurchase Invoice Item` as pi ON pi.project = pro.name
			left join `tabPurchase Invoice` as p ON p.name = pi.parent
			where pi.docstatus = 1 {condition}
			Group By pro.name
	""", as_dict = 1)

	po_condition = ''
	if filters.get("project"): 
		po_condition += f" and pro.name = '{filters.get('project')}'"

	po_data = frappe.db.sql("""
			Select pro.name,
			sum(po.base_net_amount) as po_net_total
			From `tabProject` as pro
			Left Join `tabPurchase Order Item` as po ON po.project = pro.name
			Left Join `tabPurchase Order` as p ON p.name = po.parent
			where po.docstatus = 1 and p.workflow_state = 'Approved'
			Group By pro.name
	""", as_dict = 1)
	
	po_data_map = {}
	for row in po_data:
		po_data_map[ row.name ] = { "po_net_total" : row.po_net_total }

	for row in pi_data:
		if po_data_map.get(row.name):
			row.update(po_data_map.get(row.name))
		estimated_costing = row.get("estimated_costing") or 0
		total_purchase_cost = row.get("total_purchase_cost") or 0
		po_net_total = row.get("po_net_total") or 0
		row.update({"project_balance" : estimated_costing - total_purchase_cost - po_net_total })
	return pi_data

def get_columns(filters):
	columns = [
		{
			"fieldname" : "name",
			"fieldtype" : "Link",
			"label" : "Project ID",
			"options" : "Project",
			"width" : 150
		},
		{
			"fieldname" : "project_name",
			"fieldtype" : "Data",
			"label" : "Project Name",
			"width" : 250
		},
		{
			"fieldname" : "estimated_costing",
			"fieldtype" : "Currency",
			"label" : "Estimated Cost"
		},
		{
			
			"fieldname" : "total_purchase_cost",
			"fieldtype" : "Currency",
			"label" : "Total Purchase Cost (via Purchase Invoice)"
		},
		{
			"fieldname" : "po_net_total",
			"fieldtype" : "Currency",
			"label" : "Approved PO Net Total",
			"width" : 150
		},
		{
			"fieldname" : "project_balance",
			"fieldtype" : "Currency",
			"label" : "Project Balance",
			"width" : 150
		},
	]
	return columns