import frappe
from erpnext.accounts.doctype.payment_entry.payment_entry import PaymentEntry
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from erpnext.accounts.general_ledger import make_gl_entries, process_gl_map
from vesta_si_erpnext.overrides.account_controller import make_exchange_gain_loss_journal

#Remove After Override , This is overrided to create auto exchange gain loss jv
class CustomPaymentEntry(PaymentEntry):
	def calculate_base_allocated_amount_for_reference(self, d) -> float:
		base_allocated_amount = 0
		if d.reference_doctype in frappe.get_hooks("advance_payment_doctypes"):
			# When referencing Sales/Purchase Order, use the source/target exchange rate depending on payment type.
			# This is so there are no Exchange Gain/Loss generated for such doctypes

			exchange_rate = 1
			if self.payment_type == "Receive":
				exchange_rate = self.source_exchange_rate
			elif self.payment_type == "Pay":
				exchange_rate = self.target_exchange_rate

			base_allocated_amount += flt(
				flt(d.allocated_amount) * flt(exchange_rate), self.precision("base_paid_amount")
			)
		else:
			exchange_rate = 1
			if self.payment_type == "Receive":
				exchange_rate = self.source_exchange_rate
			elif self.payment_type == "Pay":
				exchange_rate = self.target_exchange_rate

			base_allocated_amount += flt(
				flt(d.allocated_amount) * flt(exchange_rate), self.precision("base_paid_amount")
			)
			
			# on rare case, when `exchange_rate` is unset, gain/loss amount is incorrectly calculated
			# for base currency transactions
			if d.exchange_rate is None:
				d.exchange_rate = 1

			allocated_amount_in_pe_exchange_rate = flt(
				flt(d.allocated_amount) * flt(d.exchange_rate), self.precision("base_paid_amount")
			)
			d.exchange_gain_loss = base_allocated_amount - allocated_amount_in_pe_exchange_rate
		return base_allocated_amount

	def make_gl_entries(self, cancel=0, adv_adj=0):
		gl_entries = self.build_gl_map()
		gl_entries = process_gl_map(gl_entries)
		make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj)
		if cancel:
			cancel_exchange_gain_loss_journal(frappe._dict(doctype=self.doctype, name=self.name))
		else:
			make_exchange_gain_loss_journal(self)