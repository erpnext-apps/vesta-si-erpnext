import frappe
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year

#Remove After Update
def cancel_exchange_gain_loss_journal(
	parent_doc: dict | object, referenced_dt: str | None = None, referenced_dn: str | None = None
) -> None:
	"""
	Cancel Exchange Gain/Loss for Sales/Purchase Invoice, if they have any.
	"""
	if parent_doc.doctype in ["Sales Invoice", "Purchase Invoice", "Payment Entry", "Journal Entry"]:
		journals = frappe.db.get_all(
			"Journal Entry Account",
			filters={
				"reference_type": parent_doc.doctype,
				"reference_name": parent_doc.name,
				"docstatus": 1,
			},
			fields=["parent"],
			as_list=1,
		)

		if journals:
			gain_loss_journals = frappe.db.get_all(
				"Journal Entry",
				filters={
					"name": ["in", [x[0] for x in journals]],
					"voucher_type": "Exchange Gain Or Loss",
					"docstatus": 1,
				},
				as_list=1,
			)
			for doc in gain_loss_journals:
				gain_loss_je = frappe.get_doc("Journal Entry", doc[0])
				if referenced_dt and referenced_dn:
					references = [(x.reference_type, x.reference_name) for x in gain_loss_je.accounts]
					if (
						len(references) == 2
						and (referenced_dt, referenced_dn) in references
						and (parent_doc.doctype, parent_doc.name) in references
					):
						# only cancel JE generated against parent_doc and referenced_dn
						gain_loss_je.cancel()
				else:
					gain_loss_je.cancel()

#Remove After update
def create_gain_loss_journal(
	company,
	posting_date,
	party_type,
	party,
	party_account,
	gain_loss_account,
	exc_gain_loss,
	dr_or_cr,
	reverse_dr_or_cr,
	ref1_dt,
	ref1_dn,
	ref1_detail_no,
	ref2_dt,
	ref2_dn,
	ref2_detail_no,
	cost_center,
	dimensions,
) -> str:
	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.voucher_type = "Exchange Gain Or Loss"
	journal_entry.company = company
	journal_entry.posting_date = posting_date or nowdate()
	journal_entry.multi_currency = 1
	journal_entry.is_system_generated = True

	party_account_currency = frappe.get_cached_value("Account", party_account, "account_currency")

	if not gain_loss_account:
		frappe.throw(_("Please set default Exchange Gain/Loss Account in Company {}").format(company))
	gain_loss_account_currency = get_account_currency(gain_loss_account)
	company_currency = frappe.get_cached_value("Company", company, "default_currency")

	if gain_loss_account_currency != company_currency:
		frappe.throw(_("Currency for {0} must be {1}").format(gain_loss_account, company_currency))

	journal_account = frappe._dict(
		{
			"account": party_account,
			"party_type": party_type,
			"party": party,
			"account_currency": party_account_currency,
			"exchange_rate": 0,
			"cost_center": cost_center or erpnext.get_default_cost_center(company),
			"reference_type": ref1_dt,
			"reference_name": ref1_dn,
			"reference_detail_no": ref1_detail_no,
			dr_or_cr: abs(exc_gain_loss),
			dr_or_cr + "_in_account_currency": 0,
		}
	)
	if dimensions:
		journal_account.update(dimensions)
	journal_entry.append("accounts", journal_account)

	journal_account = frappe._dict(
		{
			"account": gain_loss_account,
			"account_currency": gain_loss_account_currency,
			"exchange_rate": 1,
			"cost_center": cost_center or erpnext.get_default_cost_center(company),
			"reference_type": ref2_dt,
			"reference_name": ref2_dn,
			"reference_detail_no": ref2_detail_no,
			reverse_dr_or_cr + "_in_account_currency": 0,
			reverse_dr_or_cr: abs(exc_gain_loss),
		}
	)
	if dimensions:
		journal_account.update(dimensions)
	journal_entry.append("accounts", journal_account)

	journal_entry.save()
	journal_entry.submit()
	return journal_entry.name