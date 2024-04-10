import frappe
from frappe import _

def validate_manufactured_row_material(self, method):
    error_data = []
    if self.stock_entry_type in ["Manufacture",'Repack']:
        for row in self.items:
            if (row.is_finished_item == 0 or row.is_scrap_item) and not row.s_warehouse:
                error_data.append(row)

    if error_data:
        message  = '<b>Note: Please specify the source warehouse for the raw materials listed below.</b> <br><br>'
        for row in error_data:
            message += f"<p>Row #{row.idx}:- Raw material <span style='color:red; font-weight: bold;'>{row.item_code} {row.qty} quantity</span> has been manufactured in <span style='color:red; font-weight: bold;'>{row.t_warehouse} </span> warehouse.</p><br>"

        if message:
            frappe.throw(
                msg= message,
                title=_("Warning"),
            )

