import frappe
import json
from frappe.utils import now
from datetime import datetime
from vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_invoice import validate_currency

def validate(self , method):
    validate_currency(self)
    if currency := frappe.db.get_value("Supplier", self.supplier, "default_currency"):
        if currency != self.currency:
            frappe.throw("Supplier base currency is {0}, Kindly create an invoice in <b>{0}</b>. Or Create new supplier with billing currency {1}".format(currency, self.currency))
    if not self.custom_level_1_approval_pending and self.workflow_state =="Level 1 Approval Pending":
        self.custom_level_1_approval_pending = now()
    if not self.custom_level_2_approval_pending and self.workflow_state == "Level 2 Approval Pending":
        self.custom_level_2_approval_pending = now()
    if not self.custom_approved and self.workflow_state == "Approved":
        self.custom_approved = now()
    if not self.custom_approved_and_reviewed and self.workflow_state == "Approved and Reviewed":
        self.custom_approved_and_reviewed = now()
    if not self.custom_rejected and self.workflow_state == "Rejected":
        self.custom_rejected = now()



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    if isinstance(filters, str):
        filters = json.loads(filters)

    return frappe.db.sql("""
        Select aoi.item, item.item_group, item.stock_uom
        From `tabAllow Overbill Item`  as aoi
        Left Join `tabItem` as item ON aoi.item = item.name
        Where aoi.parenttype = 'Accounts Settings' and aoi.parentfield = 'overbill_items'
    """, as_dict = as_dict)


# remove the items which is mentioned in account settings
@frappe.whitelist()
def remove_items_(items):
    if isinstance(items, str):
        items = json.loads(items)

    ac_doc = frappe.get_doc("Accounts Settings", "Accounts Settings")
    ac_items = []
    for row in ac_doc.overbill_items:
        ac_items.append(row.item)
    new_items = []
    for row in items:
        if row.get("item_code") not in ac_items:
            new_items.append(row)
    return new_items
