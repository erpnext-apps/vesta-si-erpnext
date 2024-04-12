import frappe
from frappe import _

def validate_manufactured_row_material(self, method):
    error_data = []
    missing_data = []
    if self.stock_entry_type in ["Manufacture",'Repack']:
        for row in self.items:
            if (row.is_finished_item == 0 and row.is_scrap_item == 0) and not row.s_warehouse:
                error_data.append(row)
            if not row.s_warehouse and not (row.is_finished_item or row.is_scrap_item):
                frappe.throw(f"Row #{row.idx}:- Please enable <b style='color:red;'>Is Finished Item</b> or <b style='color:red;'>Is Scrap Item</b> when source warehouse left blank")

    if error_data:
        message  = '<b>Note: Please specify the source warehouse for the raw materials listed below.</b> <br><br>'
        for row in error_data:
            message += f"<p>Row #{row.idx}:- Raw material <span style='color:red; font-weight: bold;'>{row.item_code} {row.qty} quantity</span> has been manufactured in <span style='color:red; font-weight: bold;'>{row.t_warehouse} </span> warehouse.</p><br>"

        if message:
            frappe.throw(
                msg= message,
                title=_("Warning"),
            )

