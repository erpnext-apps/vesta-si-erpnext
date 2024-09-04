# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _, throw
from frappe.model.mapper import get_mapped_doc
from frappe.query_builder.functions import Sum
from frappe.utils import cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate

import erpnext
from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	get_total_in_party_account_currency,
	is_overdue,
	update_linked_doc,
	validate_inter_company_party,
)

from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice

class CustomPurchaseInvoice(PurchaseInvoice):
	def make_supplier_gl_entry(self, gl_entries):
		# Checked both rounding_adjustment and rounded_total
		# because rounded_total had value even before introduction of posting GLE based on rounded total
		grand_total = (
			self.rounded_total if (self.rounding_adjustment and self.rounded_total) else self.grand_total
		)
		base_grand_total = flt(
			self.base_rounded_total
			if (self.base_rounding_adjustment and self.base_rounded_total)
			else self.base_grand_total,
			self.precision("base_grand_total"),
		)
		
		if grand_total and not self.is_internal_transfer():
			against_voucher = self.name
			if self.is_return and self.return_against and not self.update_outstanding_for_self:
				against_voucher = self.return_against
			# Did not use base_grand_total to book rounding loss gle
			gl_entries.append(
				self.get_gl_dict(
					{
						"account": self.credit_to,
						"party_type": "Supplier",
						"party": self.supplier,
						"due_date": self.due_date,
						"against": self.against_expense_account,
						"credit": base_grand_total,
						"credit_in_account_currency": base_grand_total
						if self.party_account_currency == self.company_currency
						else grand_total,
						"against_voucher": against_voucher,
						"against_voucher_type": self.doctype,
						"project": self.project,
						"cost_center": self.cost_center,
					},
					self.party_account_currency,
					item=self,
				)
			)

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			if self.get("amended_from"):
				self.status = "Draft"
			return

		outstanding_amount = flt(self.outstanding_amount, self.precision("outstanding_amount"))
		total = get_total_in_party_account_currency(self)

		if not status:
			if self.docstatus == 2:
				status = "Cancelled"
			elif self.docstatus == 1:
				if self.is_internal_transfer():
					self.status = "Internal Transfer"
				elif is_overdue(self, total):
					self.status = "Overdue"
				elif 0 < outstanding_amount < total:
					self.status = "Partly Paid"
				elif outstanding_amount > 0 and getdate(self.due_date) >= getdate():
					self.status = "Unpaid"
				# Check if outstanding amount is 0 due to debit note issued against invoice
				elif (
					outstanding_amount <= 0
					and self.is_return == 0
					and frappe.db.get_value(
						"Purchase Invoice", {"is_return": 1, "return_against": self.name, "docstatus": 1}
					)
				):
					self.status = "Debit Note Issued"
				elif self.is_return == 1:
					self.status = "Return"
				elif outstanding_amount <= 0:
					self.status = "Paid"
				else:
					self.status = "Submitted"
			else:
				self.status = "Draft"

		if update:
			if self.status == 'Paid' and self.doctype == "Purchase Invoice":
				self.db_set('workflow_state', self.status)
			self.db_set("status", self.status, update_modified=update_modified)
