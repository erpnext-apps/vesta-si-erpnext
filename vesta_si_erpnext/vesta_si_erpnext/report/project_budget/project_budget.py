# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	pi_data = frappe.db.sql("""
			Select pro.name, 
			pro.project_name, 
			pro.estimated_costing, 
			pro.total_purchase_cost, 
			pro.percent_complete,
			sum(pi.base_net_total) as pi_net_total
			From `tabProject` as pro
			left join `tabPurchase Invoice` as pi ON pi.project = pro.name
			where pi.docstatus = 1
			Group By pro.name
	""", as_dict = 1)

	po_data = frappe.db.sql("""
			Select pro.name,
			sum(po.base_net_total) as po_net_total
			From `tabProject` as pro
			Left Join `tabPurchase Order` as po ON po.project = pro.name
			where po.docstatus = 1 and po.workflow_state = 'Approved'
			Group By pro.name
	""", as_dict = 1)
	
	po_data_map = {}
	for row in po_data:
		po_data_map[ row.name ] = { "po_net_total" : row.po_net_total }

	for row in pi_data:
		if po_data_map.get(row.name):
			row.update(po_data_map.get(row.name))
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
			"fieldname" : "percent_complete",
			"fieldtype" : "Percentage",
			"label" : "Completed"
		},
		{
			"fieldname" : "pi_net_total",
			"fieldtype" : "Currency",
			"label" : "PI Net Total",
			"width" : 150
		},
		{
			"fieldname" : "po_net_total",
			"fieldtype" : "Currency",
			"label" : "Approved PO Net Total",
			"width" : 150
		}
	]
	return columns