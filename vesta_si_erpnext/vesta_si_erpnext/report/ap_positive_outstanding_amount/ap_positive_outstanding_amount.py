# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport


def execute(filters=None):
	args = {
		"account_type": "Payable",
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	data = ReceivablePayableReport(filters).run(args)
	data = list(data)
	positive_outstanding = []

	unblock_invoices = frappe.db.sql(f"""
					Select name, workflow_state, status
					From `tabPurchase Invoice` 
					Where due_date <= '{filters.get("report_date")}' and workflow_state != 'Blocked'
	""", as_dict=1)


	unblock_map = {}

	for row in unblock_invoices:
		unblock_map[row.name] = row


	for row in data[1]:
		if row.outstanding > 0 and row.voucher_type != "Journal Entry" and row.workflow_state != "Blocked":
			if unblock_map.get(row.voucher_no):
				row.update({"workflow_state" : unblock_map.get(row.voucher_no).get("workflow_state"), "status" : unblock_map.get(row.voucher_no).get("status")})
				positive_outstanding.append(row)
			
	
	data[1] = positive_outstanding

	data[0].insert(8, 
		{
			"fieldname" : "workflow_state",
			"fieldtype" : "Data",
			"label" : "Approval Status",
			"width":150
		}
	)
	data[0].insert(9, 
		{
			"fieldname" : "status",
			"fieldtype" : "Data",
			"label" : "Default Status",
			"width":150
		}
	)

	return data
	
