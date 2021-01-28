# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
import json
from frappe import _
from six import string_types
from collections import defaultdict
from frappe.utils import cint, flt

def validate_events(doc, method=None):
	accept_reject_inspection(doc)

def on_submit_events(doc, method=None):
	validate_analysis(doc)

	if doc.reference_type == "Stock Entry":
		update_qc_reference_as_per_frequency(doc)

def accept_reject_inspection(doc):
	if not doc.product_analysis:
		if any(reading.status == "Rejected" for reading in doc.readings):
			doc.status = "Rejected"
		else:
			doc.status = "Accepted"

def validate_analysis(doc):
	if doc.product_analysis:
		if not doc.analysed_item_code:
			frappe.throw(_("{0} is required in the Analysis Summary.")
				.format(frappe.bold("Analysed Item Code")),
				title=_("Required"))

		if doc.item_code != doc.analysed_item_code:
			frappe.throw(_("Item Code must be the same as Analysed Item Code."),
				title=_("Mismatch"))

def update_qc_reference_as_per_frequency(doc):
	if not doc.analysis_frequency or not doc.batch_no: return
	ref_doc = frappe.get_doc(doc.reference_type, doc.reference_name)

	batch_idx = None
	for row in ref_doc.get("items"):
		# search for drum that was analysed
		# to update next n drum rows
		if row.get("batch_no") == doc.batch_no:
			batch_idx = (row.idx - 1) if row.idx else row.idx
			break

	for row in ref_doc.get("items")[batch_idx : (batch_idx + doc.analysis_frequency)]:
		batch_item = frappe.db.get_value("Batch", doc.batch_no, "item")
		# before submit the whole set of drums must be of the same item in the batch
		# this is to avoid accidentally updating rows of a different item
		if row.item_code == batch_item:
			row.quality_inspection = doc.name
			if row.item_code != doc.item_code: # analysis determines it is a different item
				row.item_code = doc.item_code
				row.is_scrap_item = 1
				row.is_finished_item = 0
				row.bom_no = ""

	# to run validate method and set missing data
	ref_doc.save()

@frappe.whitelist()
def fetch_analysis_priority_list(item=None, template=None):
	if not template:
		template = frappe.db.get_value('Item', item, 'quality_inspection_template')

	if not template: return

	priority_list =  frappe.get_all('Analysis Priority',
		fields=["item_code", "inspection_template"],
		filters={'parenttype': 'Quality Inspection Template', 'parent': template},
		order_by="idx")

	return priority_list

@frappe.whitelist()
def run_analysis(readings=None, priority_list=None):
	priority_list = convert_from_string(priority_list)
	readings = convert_from_string(readings)

	if not priority_list: return

	summary = []
	for analysis in priority_list:
		if not analysis.get("inspection_template"): continue

		status, rejected_params = analyse_item(readings, analysis["inspection_template"])
		rejected_params = ','.join(rejected_params)

		summary.append({
			"analysis_item_code": analysis["analysis_item_code"],
			"inspection_template": analysis["inspection_template"],
			"status": status,
			"rejected_parameters": rejected_params
		})

	return summary

def analyse_item(readings, template):
	template_params = get_template_details(template)

	results, rejected_params = [], []
	for reading in readings:
		# inspect every input reading parameter/specification
		reading = frappe._dict(reading)
		inspection_criteria = template_params[reading.specification]

		if inspection_criteria:
			reading_status = inspect_reading(reading, inspection_criteria)
			results.append(reading_status)
			if not reading_status:
				rejected_params.append(reading.specification)

	falsy = any(result == False for result in results) # check if a single check has failed
	status = "Rejected" if falsy else "Accepted"
	return status, rejected_params

def inspect_reading(reading, inspection_criteria):
	if reading.formula_based_criteria:
		return status_based_on_acceptance_formula(reading, inspection_criteria)
	else:
		# if not formula based check acceptance values set
		return status_based_on_acceptance_values(reading, inspection_criteria)

def status_based_on_acceptance_values(reading, inspection_criteria):
	if cint(reading.non_numeric):
			return reading.get("reading_value") == inspection_criteria.get("value")
	else:
		# numeric readings
		result_1, result_2 = None, None
		reading_1, reading_2 = reading.get("reading_1"), reading.get("reading_2")

		min_value = inspection_criteria.get("min_value")
		max_value = inspection_criteria.get("max_value")

		result_1 = flt(min_value) <= flt(reading_1) <= flt(max_value) # mandatory reading

		if reading_2 is not None and reading_2.strip(): # optional reading can be left blank
			result_2 = flt(min_value) <= flt(reading_2) <= flt(max_value)

		if result_1 and result_2 is not False:
			return True
		else:
			return False

def status_based_on_acceptance_formula(reading, inspection_criteria):
	if not inspection_criteria.acceptance_formula:
			frappe.throw(_("Row #{0}: Acceptance Criteria Formula is required.").format(reading.idx),
				title=_("Missing Formula"))

	condition = inspection_criteria.acceptance_formula
	data = get_formula_evaluation_data(reading)

	try:
		result = frappe.safe_eval(condition, None, data)
		return True if result else False
	except NameError as e:
		field = frappe.bold(e.args[0].split()[1])
		frappe.throw(_("Row #{0}: {1} is not a valid reading field. Please refer to the field description.")
			.format(reading.idx, field),
			title=_("Invalid Formula"))
	except Exception:
		frappe.throw(_("Row #{0}: Acceptance Criteria Formula is incorrect.").format(reading.idx),
			title=_("Invalid Formula"))

def get_formula_evaluation_data(reading):
	data = {}
	if cint(reading.non_numeric):
		data = {"reading_value": reading.get("reading_value")}
	else:
		# numeric readings
		data["reading_1"] = flt(reading.get("reading_1"))
		data["reading_2"] = flt(reading.get("reading_2"))
		data["mean"] = (flt(reading.get("reading_1")) + flt(reading.get("reading_2"))) / 2

	return data

@frappe.whitelist()
def get_template_details(template):
	param_wise_inspection = defaultdict(dict)

	data =  frappe.get_all('Item Quality Inspection Parameter',
		fields=["specification", "value", "acceptance_formula",
			"non_numeric", "formula_based_criteria", "min_value", "max_value"],
		filters={'parenttype': 'Quality Inspection Template', 'parent': template},
		order_by="idx")

	for row in data:
		param_wise_inspection[row.specification] = row

	return param_wise_inspection

def convert_from_string(value):
	if isinstance(value, string_types):
		return json.loads(value)

	return value