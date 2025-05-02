# Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import nowdate, getdate, flt
import datetime
import calendar

import math

from frappe import _
from frappe.utils import (
    add_days,
    add_months,
    add_years,
    cint,
    date_diff,
    flt,
    get_datetime,
    get_last_day,
    getdate,
    month_diff,
    nowdate,
    today,
    unique
)
from collections import defaultdict
from frappe import scrub
from frappe.desk.reportview import get_filters_cond, get_match_cond
from erpnext.stock.get_item_details import _get_item_tax_template
import erpnext
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.accounts.utils import get_fiscal_year
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.controllers.accounts_controller import AccountsController

def install_pandas():
    try:
        import pandas
        print("Pandas is already installed.")
    except ImportError:
        print("Pandas is not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "pandas"])
            subprocess.check_call(["pip", "install", "pysftp"])
            print("Pandas has been successfully installed.")
        except Exception as e:
            print("Error occurred while installing Pandas:", e)

@frappe.whitelist()
def get_penalty_cost_paid_suppliers(filters):
    filters = json.loads(filters)
    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(getdate(),as_dict =1)

    if not filters.get("from_date") and not filters.get("to_date"):
        from_date = str(current_year.year_start_date)
        to_date = str(current_year.year_end_date)
    else:
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")

    cond = ''
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
    cond += f" and pi.posting_date >= '{from_date}'"
    cond += f" and pi.posting_date <= '{to_date}'"
    data = frappe.db.sql(f"""
            Select count(pi.supplier) as number_of_supplier
            from `tabPurchase Invoice` as pi
            left join `tabPurchase Invoice Item` as pii ON pi.name = pii.parent
            where pi.docstatus = 1  {cond}
            Group By pi.supplier
        """,as_dict = True) 
    
    return {
                "value": flt(len(data)),
                "fieldtype": "Float",
            }

@frappe.whitelist()
def get_total_penalty_cost_remitted_to_suppliers(filters):
    filters = json.loads(filters)

    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(nowdate(),as_dict =1)
    if not filters.get("from_date") and not filters.get("to_date"):
        from_date = str(current_year.year_start_date)
        to_date = str(current_year.year_end_date)
    else:
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")

    cond = ''
    if filters.get('company'):
        cond += f" and pi.company = '{filters.get('company')}'"
    if filters.get('expense_account'):
        cond += f" and pii.expense_account in ( '{filters.get('expense_account')}', '824502 - Interest expense due to late payment - 9150', '824501 - Interest expense on taxes and charges - 9150' )"
    
    cond += f" and pi.posting_date >= '{from_date}'"

    cond += f" and pi.posting_date <= '{to_date}'"
    data = frappe.db.sql(f"""
            Select sum(pii.base_net_amount) as base_net_amount, pi.name, pii.expense_account
            From `tabPurchase Invoice` as pi
            left Join `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
            Where pi.docstatus = 1 {cond}
    """,as_dict = 1)
    return {
                "value": flt(data[0].get('base_net_amount')) if data else 0,
                "fieldtype": "Currency",
            }

@frappe.whitelist()
def get_total_penalty_cost_remitted_to_suppliers_monthly(filters):
    filters = json.loads(filters)
    current_date = getdate()
    from_date = current_date.replace(day=1)
    to_date = current_date.replace(day=calendar.monthrange(current_date.year, current_date.month)[1])

    cond = ''
    if filters.get('company'):
        cond += f" and pi.company = '{filters.get('company')}'"
    if filters.get('expense_account'):
        cond += f" and pii.expense_account in ( '{filters.get('expense_account')}', '824502 - Interest expense due to late payment - 9150', '824501 - Interest expense on taxes and charges - 9150' )"
   
    cond += f" and pi.posting_date >= '{from_date}'"

    cond += f" and pi.posting_date <= '{to_date}'"

    data = frappe.db.sql(f"""
            Select sum(pii.base_net_amount) as base_net_amount, pi.name
            From `tabPurchase Invoice` as pi
            left Join `tabPurchase Invoice Item` as pii ON pii.parent = pi.name
            Where pi.docstatus = 1 {cond}
    """,as_dict = 1)

    return {
                "value": data[0].get('base_net_amount') if data and data[0].get('base_net_amount') else 0,
                "fieldtype": "Currency",
            }

#Remove After Update
#Override from asset.py
# def get_straight_line_or_manual_depr_amount(
#     asset, row, schedule_idx, number_of_pending_depreciations
# ):
#     if row.shift_based:
#         return get_shift_depr_amount(asset, row, schedule_idx)

#     # if the Depreciation Schedule is being modified after Asset Repair due to increase in asset life and value
#     if asset.flags.increase_in_asset_life:
#         return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / (
#             date_diff(asset.to_date, asset.available_for_use_date) / 365
#         )
#     # if the Depreciation Schedule is being modified after Asset Repair due to increase in asset value
#     elif asset.flags.increase_in_asset_value_due_to_repair:
#         return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / flt(
#             number_of_pending_depreciations
#         )
#     # if the Depreciation Schedule is being modified after Asset Value Adjustment due to decrease in asset value
#     elif asset.flags.decrease_in_asset_value_due_to_value_adjustment:
#         if row.daily_prorata_based:
#             daily_depr_amount = (
#                 flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
#             ) / date_diff(get_last_day(add_months(
#                         row.depreciation_start_date,
#                         flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked - 1)
#                         * row.frequency_of_depreciation,
#                     )
#                 ),
#                 add_days(
#                     get_last_day(
#                         add_months(
#                             row.depreciation_start_date,
#                             flt(
#                                 row.total_number_of_depreciations
#                                 - asset.number_of_depreciations_booked
#                                 - number_of_pending_depreciations
#                                 - 1
#                             )
#                             * row.frequency_of_depreciation,
#                         )
#                     ),
#                     1,
#                 ),
#             )

#             to_date = get_last_day(
#                 add_months(row.depreciation_start_date, schedule_idx * row.frequency_of_depreciation)
#             )
#             from_date = add_days(
#                 get_last_day(
#                     add_months(row.depreciation_start_date, (schedule_idx - 1) * row.frequency_of_depreciation)
#                 ),
#                 1,
#             )

#             return daily_depr_amount * (date_diff(to_date, from_date) + 1)
#         else:
#             return (
#                 flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
#             ) / number_of_pending_depreciations
#     # if the Depreciation Schedule is being prepared for the first time
#     else:
#         if row.daily_prorata_based:
#             daily_depr_amount = (
#                 flt(asset.gross_purchase_amount)
#                 - flt(asset.opening_accumulated_depreciation)
#                 - flt(row.expected_value_after_useful_life)
#             ) / date_diff(
#                 get_last_day(
#                     add_months(
#                         row.depreciation_start_date,
#                         flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked - 1)
#                         * row.frequency_of_depreciation,
#                     )
#                 ),
#                 add_days(
#                     get_last_day(add_months(row.depreciation_start_date, -1 * row.frequency_of_depreciation)), 1
#                 ),
#             )

#             to_date = get_last_day(
#                 add_months(row.depreciation_start_date, schedule_idx * row.frequency_of_depreciation)
#             )
#             from_date = add_days(
#                 get_last_day(
#                     add_months(row.depreciation_start_date, (schedule_idx - 1) * row.frequency_of_depreciation)
#                 ),
#                 1,
#             )

#             return daily_depr_amount * (date_diff(to_date, from_date) + 1)
#         else:
#             return (
#                 flt(asset.gross_purchase_amount)
#                 - flt(asset.opening_accumulated_depreciation)
#                 - flt(row.expected_value_after_useful_life)
#             ) / flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked)


#This Function help to filter a item tax template in update item child table
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_tax_template(doctype, txt, searchfield, start, page_len, filters):
	item_doc = frappe.get_doc("Item", filters.get("item_code"))
	item_group = item_doc.get('item_group')
	company = filters.get("company")
	taxes = item_doc.taxes or []

	while item_group:
		item_group_doc = frappe.get_doc("Item Group", item_group)
		taxes += item_group_doc.taxes or []
		item_group = item_group_doc.parent_item_group

	if not taxes:
		return frappe.get_all(
			"Item Tax Template", filters={"disabled": 0, "company": company}, as_list=True
		)
	else:
		valid_from = filters.get("valid_from")
		valid_from = valid_from[1] if isinstance(valid_from, list) else valid_from

		args = {
			"item_code": filters.get("item_code"),
			"posting_date": valid_from,
			"tax_category": filters.get("tax_category"),
			"company": company,
		}

		taxes = _get_item_tax_template(args, taxes, for_validate=True)
		return [(d,) for d in set(taxes)]


# def validate_tag_link(self, method):
#     if self.document_type == "Purchase Order" and frappe.session.user not in ["lijee.twinkle@skf.com"]:
#         frappe.throw("Only {0} can attach a tag on Purchase Order document".format(frappe.db.get_value("User", "lijee.twinkle@skf.com", 'full_name')))

#Cron every 1st of the month


def get_purchase_receipt():
    from frappe.utils import add_days, today
    from vesta_si_erpnext.vesta_si_erpnext.report.received_items_to_be_billed___vesta_si.received_items_to_be_billed___vesta_si import execute

    pr = [] 

    pr += execute( filters = { "to_date" : add_days(today(), -1), "account" :  "222503 - Goods & services received/Invoice received - non SKF - 9150"} )[1]

    number_of_pr_to_billed = len(pr)
    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(getdate(),as_dict =1)
    if doc_name := frappe.db.exists("GRIR Purchase Receipts to be Billed", current_year.name):
        doc = frappe.get_doc("GRIR Purchase Receipts to be Billed", doc_name)
        doc.append("grir_to_bill", {
            "date" : today(),
            "month" : getdate().strftime("%B"),
            "purchase_receipts_to_be_billed" : len(pr)
        })
        doc.save()
        frappe.db.commit()
    else:
        doc = frappe.get_doc({
            "doctype" : "GRIR Purchase Receipts to be Billed",
            "fiscal_year" : current_year.name,
            "grir_to_bill" : [
                {
                    "date" : today(),
                    "month" : getdate().strftime("%B"),
                    "purchase_receipts_to_be_billed" : len(pr)
                }
            ]
        })
        doc.insert()
        frappe.db.commit()


def validate_on_delete(self):
    users = frappe.db.sql(f"""
        SELECT parent as name 
        FROM `tabHas Role` 
        WHERE role = 'Tag Delete' and parent = '{frappe.session.user}'
    """, as_dict=True)
    frappe.throw(str(users))
    if not users:
        frappe.throw("Not enough permission to Delete")