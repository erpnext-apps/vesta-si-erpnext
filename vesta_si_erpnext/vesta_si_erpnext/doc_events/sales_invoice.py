import frappe

@frappe.whitelist()
def get_items_from_stock_entry(stock_entry ):
    se =  frappe.parse_json(stock_entry)
    data = frappe.db.sql(f"""Select std.item_code, std.item_name , batch.batch_qty as qty , std.uom , std.basic_rate as rate, std.name as stock_entry_detail , 
                            std.batch_no , std.t_warehouse as warehouse , std.description
                            From `tabStock Entry` as se
                            Left Join `tabStock Entry Detail` as std ON std.parent = se.name and se.name = '{se.get("Stock Entry")}'
                            Left Join   `tabBatch` as batch ON std.batch_no = batch.name
                            Where std.is_finished_item = 1 and batch.batch_qty > 0 
                            """ , as_dict = 1)
                
    
    return data
