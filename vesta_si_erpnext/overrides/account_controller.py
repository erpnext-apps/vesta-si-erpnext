# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json

import frappe
from frappe import _, bold, qb, throw
from frappe.model.workflow import get_workflow_name, is_transition_condition_satisfied
from frappe.query_builder.functions import Abs, Sum
from frappe.utils import (
	add_days,
	add_months,
	cint,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
)
from vesta_si_erpnext.overrides.utils import create_gain_loss_journal
import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.doctype.pricing_rule.utils import (
	apply_pricing_rule_for_free_items,
	apply_pricing_rule_on_transaction,
	get_applied_pricing_rules,
)
from erpnext.accounts.party import (
	get_party_account,
	get_party_account_currency,
	get_party_gle_currency,
	validate_party_frozen_disabled,
)
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.buying.utils import update_last_purchase_rate
from erpnext.controllers.print_settings import (
	set_print_templates_for_item_table,
	set_print_templates_for_taxes,
)
from erpnext.controllers.sales_and_purchase_return import validate_return
from erpnext.exceptions import InvalidCurrency
from erpnext.setup.utils import get_exchange_rate
from erpnext.stock.doctype.item.item import get_uom_conv_factor
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
from erpnext.stock.get_item_details import (
	_get_item_tax_template,
	get_conversion_factor,
	get_item_details,
	get_item_tax_map,
	get_item_warehouse,
)
from erpnext.utilities.transaction_base import TransactionBase


@frappe.whitelist()
def update_child_qty_rate(parent_doctype, trans_items, parent_doctype_name, child_docname="items"):
	def check_doc_permissions(doc, perm_type="create"):
		try:
			doc.check_permission(perm_type)
		except frappe.PermissionError:
			actions = {"create": "add", "write": "update"}

			frappe.throw(
				_("You do not have permissions to {} items in a {}.").format(
					actions[perm_type], parent_doctype
				),
				title=_("Insufficient Permissions"),
			)

	def validate_workflow_conditions(doc):
		workflow = get_workflow_name(doc.doctype)
		if not workflow:
			return

		workflow_doc = frappe.get_doc("Workflow", workflow)
		current_state = doc.get(workflow_doc.workflow_state_field)
		roles = frappe.get_roles()

		transitions = []
		for transition in workflow_doc.transitions:
			if transition.next_state == current_state and transition.allowed in roles:
				if not is_transition_condition_satisfied(transition, doc):
					continue
				transitions.append(transition.as_dict())

		if not transitions:
			frappe.throw(
				_("You are not allowed to update as per the conditions set in {} Workflow.").format(
					get_link_to_form("Workflow", workflow)
				),
				title=_("Insufficient Permissions"),
			)

	def get_new_child_item(item_row):
		child_doctype = "Sales Order Item" if parent_doctype == "Sales Order" else "Purchase Order Item"
		return set_order_defaults(
			parent_doctype, parent_doctype_name, child_doctype, child_docname, item_row
		)

	def validate_quantity(child_item, new_data):
		if not flt(new_data.get("qty")):
			frappe.throw(
				_("Row # {0}: Quantity for Item {1} cannot be zero").format(
					new_data.get("idx"), frappe.bold(new_data.get("item_code"))
				),
				title=_("Invalid Qty"),
			)

		if parent_doctype == "Sales Order" and flt(new_data.get("qty")) < flt(child_item.delivered_qty):
			frappe.throw(_("Cannot set quantity less than delivered quantity"))

		if parent_doctype == "Purchase Order" and flt(new_data.get("qty")) < flt(
			child_item.received_qty
		):
			frappe.throw(_("Cannot set quantity less than received quantity"))

	def should_update_supplied_items(doc) -> bool:
		"""Subcontracted PO can allow following changes *after submit*:

		1. Change rate of subcontracting - regardless of other changes.
		2. Change qty and/or add new items and/or remove items
		        Exception: Transfer/Consumption is already made, qty change not allowed.
		"""

		supplied_items_processed = any(
			item.supplied_qty or item.consumed_qty or item.returned_qty for item in doc.supplied_items
		)

		update_supplied_items = (
			any_qty_changed or items_added_or_removed or any_conversion_factor_changed
		)
		if update_supplied_items and supplied_items_processed:
			frappe.throw(_("Item qty can not be updated as raw materials are already processed."))

		return update_supplied_items

	data = json.loads(trans_items)

	any_qty_changed = False  # updated to true if any item's qty changes
	items_added_or_removed = False  # updated to true if any new item is added or removed
	any_conversion_factor_changed = False

	sales_doctypes = ["Sales Order", "Sales Invoice", "Delivery Note", "Quotation"]
	parent = frappe.get_doc(parent_doctype, parent_doctype_name)

	check_doc_permissions(parent, "write")
	_removed_items = validate_and_delete_children(parent, data)
	items_added_or_removed |= _removed_items

	for d in data:
		new_child_flag = False

		if not d.get("item_code"):
			# ignore empty rows
			continue

		if not d.get("docname"):
			new_child_flag = True
			items_added_or_removed = True
			check_doc_permissions(parent, "create")
			child_item = get_new_child_item(d)
		else:
			check_doc_permissions(parent, "write")
			child_item = frappe.get_doc(parent_doctype + " Item", d.get("docname"))

			prev_rate, new_rate = flt(child_item.get("rate")), flt(d.get("rate"))
			prev_qty, new_qty = flt(child_item.get("qty")), flt(d.get("qty"))
			prev_con_fac, new_con_fac = flt(child_item.get("conversion_factor")), flt(
				d.get("conversion_factor")
			)
			prev_uom, new_uom = child_item.get("uom"), d.get("uom")

			if parent_doctype == "Sales Order":
				prev_date, new_date = child_item.get("delivery_date"), d.get("delivery_date")
			elif parent_doctype == "Purchase Order":
				prev_date, new_date = child_item.get("schedule_date"), d.get("schedule_date")

			rate_unchanged = prev_rate == new_rate
			qty_unchanged = prev_qty == new_qty
			uom_unchanged = prev_uom == new_uom
			conversion_factor_unchanged = prev_con_fac == new_con_fac
			any_conversion_factor_changed |= not conversion_factor_unchanged
			date_unchanged = (
				prev_date == getdate(new_date) if prev_date and new_date else False
			)  # in case of delivery note etc
			if (
				rate_unchanged
				and qty_unchanged
				and conversion_factor_unchanged
				and uom_unchanged
				and date_unchanged
			):
				continue

		validate_quantity(child_item, d)
		if flt(child_item.get("qty")) != flt(d.get("qty")):
			any_qty_changed = True

		child_item.qty = flt(d.get("qty"))
		rate_precision = child_item.precision("rate") or 2
		conv_fac_precision = child_item.precision("conversion_factor") or 2
		qty_precision = child_item.precision("qty") or 2

		if flt(child_item.billed_amt, rate_precision) > flt(
			flt(d.get("rate"), rate_precision) * flt(d.get("qty"), qty_precision), rate_precision
		):
			frappe.throw(
				_("Row #{0}: Cannot set Rate if amount is greater than billed amount for Item {1}.").format(
					child_item.idx, child_item.item_code
				)
			)
		else:
			child_item.rate = flt(d.get("rate"), rate_precision)

		if d.get("conversion_factor"):
			if child_item.stock_uom == child_item.uom:
				child_item.conversion_factor = 1
			else:
				child_item.conversion_factor = flt(d.get("conversion_factor"), conv_fac_precision)

		if d.get("uom"):
			child_item.uom = d.get("uom")
			conversion_factor = flt(
				get_conversion_factor(child_item.item_code, child_item.uom).get("conversion_factor")
			)
			child_item.conversion_factor = (
				flt(d.get("conversion_factor"), conv_fac_precision) or conversion_factor
			)

		if d.get("delivery_date") and parent_doctype == "Sales Order":
			child_item.delivery_date = d.get("delivery_date")

		if d.get("schedule_date") and parent_doctype == "Purchase Order":
			child_item.schedule_date = d.get("schedule_date")

		if flt(child_item.price_list_rate):
			if flt(child_item.rate) > flt(child_item.price_list_rate):
				#  if rate is greater than price_list_rate, set margin
				#  or set discount
				child_item.discount_percentage = 0

				if parent_doctype in sales_doctypes:
					child_item.margin_type = "Amount"
					child_item.margin_rate_or_amount = flt(
						child_item.rate - child_item.price_list_rate, child_item.precision("margin_rate_or_amount")
					)
					child_item.rate_with_margin = child_item.rate
			else:
				child_item.discount_percentage = flt(
					(1 - flt(child_item.rate) / flt(child_item.price_list_rate)) * 100.0,
					child_item.precision("discount_percentage"),
				)
				child_item.discount_amount = flt(child_item.price_list_rate) - flt(child_item.rate)

				if parent_doctype in sales_doctypes:
					child_item.margin_type = ""
					child_item.margin_rate_or_amount = 0
					child_item.rate_with_margin = 0

		child_item.flags.ignore_validate_update_after_submit = True
		if new_child_flag:
			parent.load_from_db()
			child_item.idx = len(parent.items) + 1
			child_item.insert()
		else:
			child_item.save()

	parent.reload()
	parent.flags.ignore_validate_update_after_submit = True
	parent.set_qty_as_per_stock_uom()
	parent.calculate_taxes_and_totals()
	parent.set_total_in_words()
	if parent_doctype == "Sales Order":
		make_packing_list(parent)
		parent.set_gross_profit()
	frappe.get_doc("Authorization Control").validate_approving_authority(
		parent.doctype, parent.company, parent.base_grand_total
	)

	parent.set_payment_schedule()
	if parent_doctype == "Purchase Order":
		parent.validate_minimum_order_qty()
		parent.validate_budget()
		if parent.is_against_so():
			parent.update_status_updater()
	else:
		parent.check_credit_limit()

	# reset index of child table
	for idx, row in enumerate(parent.get(child_docname), start=1):
		row.idx = idx

	parent.save()

	if parent_doctype == "Purchase Order":
		update_last_purchase_rate(parent, is_submit=1)
		parent.update_prevdoc_status()
		parent.update_requested_qty()
		parent.update_ordered_qty()
		parent.update_ordered_and_reserved_qty()
		parent.update_receiving_percentage()
		if parent.is_old_subcontracting_flow:
			if should_update_supplied_items(parent):
				parent.update_reserved_qty_for_subcontract()
				parent.create_raw_materials_supplied()
			parent.save()
	else:  # Sales Order
		parent.validate_warehouse()
		parent.update_reserved_qty()
		parent.update_project()
		parent.update_prevdoc_status("submit")
		parent.update_delivery_status()

	parent.reload()
	validate_workflow_conditions(parent)

	parent.update_blanket_order()
	parent.update_billing_percentage()
	parent.set_status()

def validate_and_delete_children(parent, data) -> bool:
	deleted_children = []
	updated_item_names = [d.get("docname") for d in data]
	for item in parent.items:
		if item.name not in updated_item_names:
			deleted_children.append(item)

	for d in deleted_children:
		validate_child_on_delete(d, parent)
		d.cancel()
		d.delete()

	# need to update ordered qty in Material Request first
	# bin uses Material Request Items to recalculate & update
	parent.update_prevdoc_status()

	for d in deleted_children:
		update_bin_on_delete(d, parent.doctype)

	return bool(deleted_children)

def validate_child_on_delete(row, parent):
	"""Check if partially transacted item (row) is being deleted."""
	if parent.doctype == "Sales Order":
		if flt(row.delivered_qty):
			frappe.throw(
				_("Row #{0}: Cannot delete item {1} which has already been delivered").format(
					row.idx, row.item_code
				)
			)
		if flt(row.work_order_qty):
			frappe.throw(
				_("Row #{0}: Cannot delete item {1} which has work order assigned to it.").format(
					row.idx, row.item_code
				)
			)
		if flt(row.ordered_qty):
			frappe.throw(
				_("Row #{0}: Cannot delete item {1} which is assigned to customer's purchase order.").format(
					row.idx, row.item_code
				)
			)

	if parent.doctype == "Purchase Order" and flt(row.received_qty):
		frappe.throw(
			_("Row #{0}: Cannot delete item {1} which has already been received").format(
				row.idx, row.item_code
			)
		)

	if flt(row.billed_amt):
		frappe.throw(
			_("Row #{0}: Cannot delete item {1} which has already been billed.").format(
				row.idx, row.item_code
			)
		)

def update_bin_on_delete(row, doctype):
	"""Update bin for deleted item (row)."""
	from erpnext.stock.stock_balance import (
		get_indented_qty,
		get_ordered_qty,
		get_reserved_qty,
		update_bin_qty,
	)

	qty_dict = {}

	if doctype == "Sales Order":
		qty_dict["reserved_qty"] = get_reserved_qty(row.item_code, row.warehouse)
	else:
		if row.material_request_item:
			qty_dict["indented_qty"] = get_indented_qty(row.item_code, row.warehouse)

		qty_dict["ordered_qty"] = get_ordered_qty(row.item_code, row.warehouse)

	if row.warehouse:
		update_bin_qty(row.item_code, row.warehouse, qty_dict)


def set_order_defaults(
	parent_doctype, parent_doctype_name, child_doctype, child_docname, trans_item
):
	"""
	Returns a Sales/Purchase Order Item child item containing the default values
	"""
	p_doc = frappe.get_doc(parent_doctype, parent_doctype_name)
	child_item = frappe.new_doc(child_doctype, p_doc, child_docname)
	item = frappe.get_doc("Item", trans_item.get("item_code"))

	for field in ("item_code", "item_name", "description", "item_group"):
		child_item.update({field: item.get(field)})

	date_fieldname = "delivery_date" if child_doctype == "Sales Order Item" else "schedule_date"
	child_item.update({date_fieldname: trans_item.get(date_fieldname) or p_doc.get(date_fieldname)})
	child_item.stock_uom = item.stock_uom
	child_item.uom = trans_item.get("uom") or item.stock_uom
	child_item.warehouse = get_item_warehouse(item, p_doc, overwrite_warehouse=True)
	conversion_factor = flt(
		get_conversion_factor(item.item_code, child_item.uom).get("conversion_factor")
	)
	child_item.conversion_factor = flt(trans_item.get("conversion_factor")) or conversion_factor
	if child_doctype == "Purchase Order Item":
		# Initialized value will update in parent validation
		child_item.update({"item_tax_template":trans_item.get('item_tax_template') })
		child_item.base_rate = 1
		child_item.base_amount = 1
	if child_doctype == "Sales Order Item":
		child_item.warehouse = get_item_warehouse(item, p_doc, overwrite_warehouse=True)
		if not child_item.warehouse:
			frappe.throw(
				_("Cannot find {} for item {}. Please set the same in Item Master or Stock Settings.").format(
					frappe.bold("default warehouse"), frappe.bold(item.item_code)
				)
			)

	set_child_tax_template_and_map(item, child_item, p_doc)
	add_taxes_from_tax_template(child_item, p_doc)
	return child_item

def add_taxes_from_tax_template(child_item, parent_doc, db_insert=True):
	add_taxes_from_item_tax_template = frappe.db.get_single_value(
		"Accounts Settings", "add_taxes_from_item_tax_template"
	)

	if child_item.get("item_tax_rate") and add_taxes_from_item_tax_template:
		tax_map = json.loads(child_item.get("item_tax_rate"))
		for tax_type in tax_map:
			tax_rate = flt(tax_map[tax_type])
			taxes = parent_doc.get("taxes") or []
			# add new row for tax head only if missing
			found = any(tax.account_head == tax_type for tax in taxes)
			if not found:
				tax_row = parent_doc.append("taxes", {})
				tax_row.update(
					{
						"description": str(tax_type).split(" - ")[0],
						"charge_type": "On Net Total",
						"account_head": tax_type,
						"rate": tax_rate,
					}
				)
				if parent_doc.doctype == "Purchase Order":
					tax_row.update({"category": "Total", "add_deduct_tax": "Add"})
				if db_insert:
					tax_row.db_insert()
                    
def set_child_tax_template_and_map(item, child_item, parent_doc):
	args = {
		"item_code": item.item_code,
		"posting_date": parent_doc.transaction_date,
		"tax_category": parent_doc.get("tax_category"),
		"company": parent_doc.get("company"),
	}

	item_tax_template = _get_item_tax_template(args, item.taxes)
	if item_tax_template:
		child_item.item_tax_template = item_tax_template
	if child_item.get("item_tax_template"):
		child_item.item_tax_rate = get_item_tax_map(
			parent_doc.get("company"), child_item.item_tax_template, as_json=True
		)
		
#Remove After Version Update (This function I have added it's not available in current version)
def make_exchange_gain_loss_journal(
		self, args: dict | None = None, dimensions_dict: dict | None = None
	) -> None:
	"""
	Make Exchange Gain/Loss journal for Invoices and Payments
	"""
	# Cancelling existing exchange gain/loss journals is handled during the `on_cancel` event.
	# see accounts/utils.py:cancel_exchange_gain_loss_journal()
	if self.docstatus == 1:
		if self.get("doctype") == "Journal Entry":
			# 'args' is populated with exchange gain/loss account and the amount to be booked.
			# These are generated by Sales/Purchase Invoice during reconciliation and advance allocation.
			# and below logic is only for such scenarios
			if args:
				precision = get_currency_precision()
				for arg in args:
					# Advance section uses `exchange_gain_loss` and reconciliation uses `difference_amount`
					if (
						flt(arg.get("difference_amount", 0), precision) != 0
						or flt(arg.get("exchange_gain_loss", 0), precision) != 0
					) and arg.get("difference_account"):
						party_account = arg.get("account")
						gain_loss_account = arg.get("difference_account")
						difference_amount = arg.get("difference_amount") or arg.get("exchange_gain_loss")
						if difference_amount > 0:
							dr_or_cr = "debit" if arg.get("party_type") == "Customer" else "credit"
						else:
							dr_or_cr = "credit" if arg.get("party_type") == "Customer" else "debit"

						reverse_dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

						if not self.gain_loss_journal_already_booked(
							gain_loss_account,
							difference_amount,
							self.doctype,
							self.name,
							arg.get("referenced_row"),
						):
							posting_date = arg.get("difference_posting_date") or frappe.db.get_value(
								arg.voucher_type, arg.voucher_no, "posting_date"
							)
							je = create_gain_loss_journal(
								self.company,
								posting_date,
								arg.get("party_type"),
								arg.get("party"),
								party_account,
								gain_loss_account,
								difference_amount,
								dr_or_cr,
								reverse_dr_or_cr,
								arg.get("against_voucher_type"),
								arg.get("against_voucher"),
								arg.get("idx"),
								self.doctype,
								self.name,
								arg.get("referenced_row"),
								arg.get("cost_center"),
								dimensions_dict,
							)
							frappe.msgprint(
								_("Exchange Gain/Loss amount has been booked through {0}").format(
									get_link_to_form("Journal Entry", je)
								)
							)

		if self.get("doctype") == "Payment Entry":
			# For Payment Entry, exchange_gain_loss field in the `references` table is the trigger for journal creation
			gain_loss_to_book = [x for x in self.references if x.exchange_gain_loss != 0]
			booked = []
			if gain_loss_to_book:
				[x.reference_doctype for x in gain_loss_to_book]
				[x.reference_name for x in gain_loss_to_book]
				je = qb.DocType("Journal Entry")
				jea = qb.DocType("Journal Entry Account")
				parents = (
					qb.from_(jea)
					.select(jea.parent)
					.where(
						(jea.reference_type == "Payment Entry")
						& (jea.reference_name == self.name)
						& (jea.docstatus == 1)
					)
					.run()
				)

				booked = []
				if parents:
					booked = (
						qb.from_(je)
						.inner_join(jea)
						.on(je.name == jea.parent)
						.select(jea.reference_type, jea.reference_name, jea.reference_detail_no)
						.where(
							(je.docstatus == 1)
							& (je.name.isin(parents))
							& (je.voucher_type == "Exchange Gain or Loss")
						)
						.run()
					)

			for d in gain_loss_to_book:
				# Filter out References for which Gain/Loss is already booked
				if d.exchange_gain_loss and (
					(d.reference_doctype, d.reference_name, str(d.idx)) not in booked
				):
					if self.payment_type == "Receive":
						party_account = self.paid_from
					elif self.payment_type == "Pay":
						party_account = self.paid_to

					dr_or_cr = "debit" if d.exchange_gain_loss > 0 else "credit"

					# Inverse debit/credit for payable accounts
					if is_payable_account(self, d.reference_doctype, party_account):
						dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

					reverse_dr_or_cr = "debit" if dr_or_cr == "credit" else "credit"

					gain_loss_account = frappe.get_cached_value(
						"Company", self.company, "exchange_gain_loss_account"
					)

					je = create_gain_loss_journal(
						self.company,
						args.get("difference_posting_date") if args else self.posting_date,
						self.party_type,
						self.party,
						party_account,
						gain_loss_account,
						d.exchange_gain_loss,
						dr_or_cr,
						reverse_dr_or_cr,
						d.reference_doctype,
						d.reference_name,
						d.idx,
						self.doctype,
						self.name,
						d.idx,
						self.cost_center,
						dimensions_dict,
					)
					frappe.msgprint(
						_("Exchange Gain/Loss amount has been booked through {0}").format(
							get_link_to_form("Journal Entry", je)
						)
					)

#Remove After Version Update
def is_payable_account(self, reference_doctype, account):
	if reference_doctype == "Purchase Invoice" or (
		reference_doctype == "Journal Entry"
		and frappe.get_cached_value("Account", account, "account_type") == "Payable"
	):
		return True
	return False