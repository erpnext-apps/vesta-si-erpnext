import frappe
import json
from erpnext.stock.doctype.putaway_rule.putaway_rule import (
	add_row, show_unassigned_items_message
)

import copy
from collections import defaultdict
from frappe import _
from frappe.utils import cint, floor, flt, nowdate

from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos
from erpnext.stock.utils import get_stock_balance


def get_acquired_warehouses(company):
	acquired_warehouses = {}

	filters = {
		"company": company,
		"disable": 0
	}

	rules = frappe.get_all("Putaway Rule",
		fields=["name", "item_code", "stock_capacity", "priority", "warehouse"],
		filters=filters,
		order_by="priority asc, capacity desc")

	for rule in rules:
		balance_qty = get_stock_balance(rule.item_code, rule.warehouse, nowdate())
		if balance_qty > 0:
			acquired_warehouses.setdefault(rule.warehouse, rule.item_code)

	return acquired_warehouses

@frappe.whitelist()
def apply_putaway_rule(doctype, items, company, sync=None, purpose=None):
	""" Applies Putaway Rule on line items.

		items: List of Purchase Receipt/Stock Entry Items
		company: Company in the Purchase Receipt/Stock Entry
		doctype: Doctype to apply rule on
		purpose: Purpose of Stock Entry
		sync (optional): Sync with client side only for client side calls
	"""
	if isinstance(items, str):
		items = json.loads(items)

	items_not_accomodated, updated_table = [], []
	item_wise_rules = defaultdict(list)

	used_capacity = {}
	acquired_warehouses = get_acquired_warehouses(company)
	for item in items:
		if isinstance(item, dict):
			item = frappe._dict(item)

		source_warehouse = item.get("s_warehouse")
		serial_nos = get_serial_nos(item.get("serial_no"))
		item.conversion_factor = flt(item.conversion_factor) or 1.0
		pending_qty, item_code = flt(item.qty), item.item_code
		pending_stock_qty = flt(item.transfer_qty) if doctype == "Stock Entry" else flt(item.stock_qty)
		uom_must_be_whole_number = frappe.db.get_value('UOM', item.uom, 'must_be_whole_number')

		if not pending_qty or not item_code:
			updated_table = add_row(item, pending_qty, source_warehouse or item.warehouse, updated_table)
			continue

		at_capacity, rules = get_ordered_putaway_rules(item_code, company, source_warehouse=source_warehouse)

		if not rules:
			if at_capacity:
				# rules available, but no free space
				items_not_accomodated.append([item_code, pending_qty])
			else:
				updated_table = add_row(item, pending_qty, warehouse, updated_table)
			continue

		# maintain item/item-warehouse wise rules, to handle if item is entered twice
		# in the table, due to different price, etc.
		key = item_code
		if doctype == "Stock Entry" and purpose == "Material Transfer" and source_warehouse:
			key = (item_code, source_warehouse)

		if not item_wise_rules[key]:
			item_wise_rules[key] = rules

		for rule in item_wise_rules[key]:
			print(acquired_warehouses, rule.warehouse)
			if rule.warehouse in acquired_warehouses and acquired_warehouses[rule.warehouse] != item_code:
				continue

			if pending_stock_qty > 0 and rule.free_space:
				stock_qty_to_allocate = flt(rule.free_space) if pending_stock_qty >= flt(rule.free_space) else pending_stock_qty
				qty_to_allocate = stock_qty_to_allocate / item.conversion_factor

				if uom_must_be_whole_number:
					qty_to_allocate = floor(qty_to_allocate)
					stock_qty_to_allocate = qty_to_allocate * item.conversion_factor

				if not qty_to_allocate: break

				acquired_warehouses.setdefault(rule.warehouse, item_code)
				updated_table = add_row(item, qty_to_allocate, rule.warehouse, updated_table,
					rule.name, serial_nos=serial_nos)

				pending_stock_qty -= stock_qty_to_allocate
				pending_qty -= qty_to_allocate
				rule["free_space"] -= stock_qty_to_allocate

				if not pending_stock_qty > 0: break

		# if pending qty after applying all rules, add row without warehouse
		if pending_stock_qty > 0:
			items_not_accomodated.append([item.item_code, pending_qty])

	if items_not_accomodated:
		show_unassigned_items_message(items_not_accomodated)

	items[:] = updated_table if updated_table else items # modify items table

	if sync and json.loads(sync): # sync with client side
		return items

def get_ordered_putaway_rules(item_code, company, source_warehouse=None):
	"""Returns an ordered list of putaway rules to apply on an item."""
	filters = {
		"item_code": item_code,
		"company": company,
		"disable": 0
	}
	if source_warehouse:
		filters.update({"warehouse": ["!=", source_warehouse]})

	rules = frappe.get_all("Putaway Rule",
		fields=["name", "item_code", "stock_capacity", "priority", "warehouse"],
		filters=filters,
		order_by="priority asc, capacity desc")

	if not rules:
		return False, None

	vacant_rules = []
	for rule in rules:
		balance_qty = get_stock_balance(rule.item_code, rule.warehouse, nowdate())
		free_space = flt(rule.stock_capacity) - flt(balance_qty)
		if free_space > 0:
			rule["free_space"] = free_space
			vacant_rules.append(rule)

	if not vacant_rules:
		# After iterating through rules, if no rules are left
		# then there is not enough space left in any rule
		return True, None

	vacant_rules = sorted(vacant_rules, key = lambda i: (i['priority'], -i['free_space']))

	return False, vacant_rules
