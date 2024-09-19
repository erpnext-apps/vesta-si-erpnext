# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport


def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	data = ReceivablePayableReport(filters).run(args)

	data = list(data)
	positive_outstanding = []
	for row in data[1]:
		if row.outstanding > 0 and age > 0:
			positive_outstanding.append(row)
	
	data[1] = positive_outstanding

	return data
	
