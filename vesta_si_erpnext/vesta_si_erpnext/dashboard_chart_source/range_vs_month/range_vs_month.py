import frappe
import json
from frappe.utils import getdate
from vesta_si_erpnext.vesta_si_erpnext.report.purchase_invoice_timeline_report.purchase_invoice_timeline_report import execute

@frappe.whitelist()
def get_data(filters=None):
    filters = json.loads(filters)
    if filters.get("fiscal_year"):
        doc = frappe.get_doc("Fiscal Year", filters.get("fiscal_year"))
        year_start_date = doc.year_start_date
        year_end_date = doc.year_end_date
        filters.update({
            "from_date" : year_start_date,
            "to_date" : year_end_date
        })
    columns, data = execute(filters)

    # Generate range labels
    ranges = [
        (0, filters.get("range1")),
        (filters.get("range1") + 1, filters.get("range2")),
        (filters.get("range2") + 1, filters.get("range3")),
        (filters.get("range3") + 1, filters.get("range4")),
        ("Above", filters.get("range4")),
    ]
    labels = ["{0} - {1}".format(*r) if r[0] != "Above" else "Above {0}".format(r[1]) for r in ranges]

    # Initialize monthly data
    monthly_data = {month: [0] * 5 for month in range(1, 13)}  # 12 months, 5 ranges each

    # Process data
    for row in data:
        month = getdate(row.get('posting_date')).month
        proce_days = row.get("proce_days")

        if proce_days is not None:
            if 0 <= proce_days <= filters.get("range1"):
                monthly_data[month][0] += 1
            elif filters.get("range1") + 1 <= proce_days <= filters.get("range2"):
                monthly_data[month][1] += 1
            elif filters.get("range2") + 1 <= proce_days <= filters.get("range3"):
                monthly_data[month][2] += 1
            elif filters.get("range3") + 1 <= proce_days <= filters.get("range4"):
                monthly_data[month][3] += 1
            elif proce_days > filters.get("range4"):
                monthly_data[month][4] += 1

    # Prepare final datasets
    months = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    datasets = [
        {"name": label, "values": [monthly_data[m + 1][i] for m in range(12)]}
        for i, label in enumerate(labels)
    ]

    return {
        "labels": months,
        "datasets": datasets,
    }
