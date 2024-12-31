import frappe
import json

@frappe.whitelist()
def get_giri_data(filters):
    filters = json.loads(filters)
    data = frappe.db.get_list('GRIR To Bill',
                                filters={
                                    'parenttype': 'GRIR Purchase Receipts to be Billed',
                                    'parent' : f"{filters.get('year')}",
                                    'fiscal_year' : f"{filters.get('year')}"
                                },
                                fields=['month', 'fiscal_year', 'date', 'purchase_receipts_to_be_billed'],
                                order_by='date'
                            )

    labels = [ row.month for row in data]
    values = [row.purchase_receipts_to_be_billed for row in data]
    return {
        "labels": labels, 
        "datasets": 
        [
            {"values": values , "name" : "GRIR Monthly Billing", "chartType" : "bar"},

        ],
       
    }
    