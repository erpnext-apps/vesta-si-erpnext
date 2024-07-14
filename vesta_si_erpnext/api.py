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
)

import erpnext
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.accounts.utils import get_fiscal_year
from erpnext.assets.doctype.asset.depreciation import (
    get_depreciation_accounts,
    get_disposal_account_and_cost_center,
    is_first_day_of_the_month,
    is_last_day_of_the_month,
)
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
            print("Pandas has been successfully installed.")
        except Exception as e:
            print("Error occurred while installing Pandas:", e)

@frappe.whitelist()
def get_penalty_cost_paid_suppliers(filters):
    from erpnext.accounts.utils import get_fiscal_year
    current_year = get_fiscal_year(nowdate(),as_dict =1)

    from_date = str(current_year.year_start_date)
    to_date = str(current_year.year_end_date)

    filters = json.loads(filters)
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

    from_date = str(current_year.year_start_date)
    to_date = str(current_year.year_end_date)

    cond = ''
    if filters.get('company'):
        cond += f" and pi.company = '{filters.get('company')}'"
    if filters.get('expense_account'):
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
    
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
        cond += f" and pii.expense_account = '{filters.get('expense_account')}'"
   
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
#Override from asset.py
def get_straight_line_or_manual_depr_amount(
    asset, row, schedule_idx, number_of_pending_depreciations
):
    if row.shift_based:
        return get_shift_depr_amount(asset, row, schedule_idx)

    # if the Depreciation Schedule is being modified after Asset Repair due to increase in asset life and value
    if asset.flags.increase_in_asset_life:
        return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / (
            date_diff(asset.to_date, asset.available_for_use_date) / 365
        )
    # if the Depreciation Schedule is being modified after Asset Repair due to increase in asset value
    elif asset.flags.increase_in_asset_value_due_to_repair:
        return (flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)) / flt(
            number_of_pending_depreciations
        )
    # if the Depreciation Schedule is being modified after Asset Value Adjustment due to decrease in asset value
    elif asset.flags.decrease_in_asset_value_due_to_value_adjustment:
        if row.daily_prorata_based:
            daily_depr_amount = (
                flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
            ) / date_diff(get_last_day(add_months(
                        row.depreciation_start_date,
                        flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked - 1)
                        * row.frequency_of_depreciation,
                    )
                ),
                add_days(
                    get_last_day(
                        add_months(
                            row.depreciation_start_date,
                            flt(
                                row.total_number_of_depreciations
                                - asset.number_of_depreciations_booked
                                - number_of_pending_depreciations
                                - 1
                            )
                            * row.frequency_of_depreciation,
                        )
                    ),
                    1,
                ),
            )

            to_date = get_last_day(
                add_months(row.depreciation_start_date, schedule_idx * row.frequency_of_depreciation)
            )
            from_date = add_days(
                get_last_day(
                    add_months(row.depreciation_start_date, (schedule_idx - 1) * row.frequency_of_depreciation)
                ),
                1,
            )

            return daily_depr_amount * (date_diff(to_date, from_date) + 1)
        else:
            return (
                flt(row.value_after_depreciation) - flt(row.expected_value_after_useful_life)
            ) / number_of_pending_depreciations
    # if the Depreciation Schedule is being prepared for the first time
    else:
        if row.daily_prorata_based:
            daily_depr_amount = (
                flt(asset.gross_purchase_amount)
                - flt(asset.opening_accumulated_depreciation)
                - flt(row.expected_value_after_useful_life)
            ) / date_diff(
                get_last_day(
                    add_months(
                        row.depreciation_start_date,
                        flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked - 1)
                        * row.frequency_of_depreciation,
                    )
                ),
                add_days(
                    get_last_day(add_months(row.depreciation_start_date, -1 * row.frequency_of_depreciation)), 1
                ),
            )

            to_date = get_last_day(
                add_months(row.depreciation_start_date, schedule_idx * row.frequency_of_depreciation)
            )
            from_date = add_days(
                get_last_day(
                    add_months(row.depreciation_start_date, (schedule_idx - 1) * row.frequency_of_depreciation)
                ),
                1,
            )

            return daily_depr_amount * (date_diff(to_date, from_date) + 1)
        else:
            return (
                flt(asset.gross_purchase_amount)
                - flt(asset.opening_accumulated_depreciation)
                - flt(row.expected_value_after_useful_life)
            ) / flt(row.total_number_of_depreciations - asset.number_of_depreciations_booked)