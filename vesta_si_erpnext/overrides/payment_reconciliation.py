import frappe
from frappe import _, msgprint, qb
from frappe.model.document import Document
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import flt, get_link_to_form, getdate, nowdate, today
import erpnext
from erpnext.accounts.doctype.process_payment_reconciliation.process_payment_reconciliation import (
	is_any_doc_running,
)
from erpnext.accounts.utils import (
	QueryPaymentLedger,
	get_outstanding_invoices,
	reconcile_against_document,
)
from erpnext.controllers.accounts_controller import get_advance_payment_entries
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import PaymentReconciliation


class customPaymentReconciliation(PaymentReconciliation):
    def get_return_invoices(self):
		voucher_type = "Sales Invoice" if self.party_type == "Customer" else "Purchase Invoice"
		doc = qb.DocType(voucher_type)

		conditions = []
		conditions.append(doc.docstatus == 1)
		conditions.append(doc[frappe.scrub(self.party_type)] == self.party)
		conditions.append(doc.is_return == 1)

		# if self.payment_name:
		# 	conditions.append(doc.name.like(f"%{self.payment_name}%"))

		self.return_invoices_query = (
			qb.from_(doc)
			.select(
				ConstantColumn(voucher_type).as_("voucher_type"),
				doc.name.as_("voucher_no"),
				doc.return_against,
			)
			.where(Criterion.all(conditions))
		)
		if self.payment_limit:
			self.return_invoices_query = self.return_invoices_query.limit(self.payment_limit)

		self.return_invoices = self.return_invoices_query.run(as_dict=True)

	def get_dr_or_cr_notes(self):
		self.build_qb_filter_conditions(get_return_invoices=True)

		ple = qb.DocType("Payment Ledger Entry")

		if erpnext.get_party_account_type(self.party_type) == "Receivable":
			self.common_filter_conditions.append(ple.account_type == "Receivable")
		else:
			self.common_filter_conditions.append(ple.account_type == "Payable")
		self.common_filter_conditions.append(ple.account == self.receivable_payable_account)

		self.get_return_invoices()

		outstanding_dr_or_cr = []
		if self.return_invoices:
			ple_query = QueryPaymentLedger()
			return_outstanding = ple_query.get_voucher_outstandings(
				vouchers=self.return_invoices,
				common_filter=self.common_filter_conditions,
				posting_date=self.ple_posting_date_filter,
				min_outstanding=-(self.minimum_payment_amount) if self.minimum_payment_amount else None,
				max_outstanding=-(self.maximum_payment_amount) if self.maximum_payment_amount else None,
				get_payments=True,
				accounting_dimensions=self.accounting_dimension_filter_conditions,
			)
		
			for inv in return_outstanding:
				if inv.outstanding != 0:
					outstanding_dr_or_cr.append(
						frappe._dict(
							{
								"reference_type": inv.voucher_type,
								"reference_name": inv.voucher_no,
								"amount": -(inv.outstanding_in_account_currency),
								"posting_date": inv.posting_date,
								"currency": inv.currency,
								"cost_center": inv.cost_center,
							}
						)
					)
		return outstanding_dr_or_cr