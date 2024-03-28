# import frappe
# from frappe import _

# def validate_manufactured_row_material(self, method):
#     error_data = []
#     if self.stock_entry_type == "Manufacture":
#         for row in self.items:
#             if row.is_finished_item == 0 and row.t_warehouse:
#                 error_data.append(row)

#     if error_data:
#         message  = ''
#         for row in error_data:
#             message += f"<p>Row material <span style='color:red; font-weight: bold;'>{row.item_code} {row.qty} quantity</span> has been manufactured in warehouse <span style='color:red; font-weight: bold;'>{row.t_warehouse}</span>.</p><br>"

#         if message:
#             frappe.msgprint(
#                 msg= message,
#                 title=_("Warning"),
#                 indicator="red",
#             )

