
import frappe
from frappe.utils import cint

def validate(doc, method = None):
    set_lowest_freqency_in_item(doc)
    
def set_lowest_freqency_in_item(doc):
    params = doc.get("item_quality_inspection_parameter")
    freqs = [param.frequency for param in params]
    freq = min(freqs)
    frappe.db.set_value("Item", doc.item_name, "analysis_frequency", cint(freq))
        
