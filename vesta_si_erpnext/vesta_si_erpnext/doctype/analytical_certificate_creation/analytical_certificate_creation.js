// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Analytical Certificate Creation', {
	onload: function (frm) {
		frm.set_query("drum", "batches", function () {
			return {
				filters: {
					item: frm.doc.item_code
				},
			};
		});
	},
	get_qi_parameters: function (frm) {
		frm.clear_table("charge_or_drum");
		let parameters = ['Iron Content - Fe (wt%)', 'Calcium Content - Ca (wt%)', 'Aluminium Content - Al (wt%)', 'Oxygen Content - O (wt%)', 'Carbon Content - C (wt%)', 'Alpha Beta%', 'Free Silicon - Si (wt%)',
			'BET%', 'Particle Size Distribution - PSD, D10 (µm)', 'Particle Size Distribution - PSD, D50 (µm)', 'Particle Size Distribution - PSD, D90 (µm)'];
		for (let parameter of parameters) {
			var row = frm.add_child("charge_or_drum");
			row.quality_inspection_paramter = parameter;
		}
		frm.refresh_field("charge_or_drum");
	}
});

frappe.ui.form.on("Analytical Certificate Drum", {
	drum: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.drum) {
			frappe.call({
				method: "vesta_si_erpnext.vesta_si_erpnext.doctype.analytical_certificate_creation.analytical_certificate_creation.get_quality_inspection_info",
				args: {
					batch_no: row.drum,
				},
				callback: function (r) {
					if (r.message) {
						let readings = r.message.readings;
						let parameters_to_set = [];
						for (let param of frm.doc.charge_or_drum) {
							if (param.fetch_from == 'Drum') {
								parameters_to_set.push(param.quality_inspection_paramter);
							}
						}
						set_qi_parameters(row, readings, parameters_to_set);
					}
				}
			});

			frappe.db.get_value('Batch', row.drum, "batch_qty", function (value) {
				frappe.model.set_value(row.doctype, row.name, 'weight', value.batch_qty);
			});
		}
	},
	charge: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.charge) {
			frappe.call({
				method: "vesta_si_erpnext.vesta_si_erpnext.doctype.analytical_certificate_creation.analytical_certificate_creation.get_quality_inspection_info",
				args: {
					batch_no: row.charge,
				},
				callback: function (r) {
					if (r.message) {
						let readings = r.message.readings;
						let parameters_to_set = [];
						for (let param of frm.doc.charge_or_drum) {
							if (param.fetch_from == 'Charge') {
								parameters_to_set.push(param.quality_inspection_paramter);
							}
						}
						set_qi_parameters(row, readings, parameters_to_set);
					}
				}
			});
		}
	}
});

function set_qi_parameters(row, readings, parameters_to_set) {
	for (let reading of readings) {
		if (parameters_to_set.includes(reading.specification)) {
			if (reading.specification == 'Iron Content - Fe (wt%)') { frappe.model.set_value(row.doctype, row.name, 'fe_wt', reading.reading_1); }
			else if (reading.specification == 'Calcium Content - Ca (wt%)') { frappe.model.set_value(row.doctype, row.name, 'ca_wt', reading.reading_1); }
			else if (reading.specification == 'Aluminium Content - Al (wt%)') { frappe.model.set_value(row.doctype, row.name, 'al_wt', reading.reading_1); }
			else if (reading.specification == 'Carbon Content - C (wt%)') { frappe.model.set_value(row.doctype, row.name, 'c_wt', reading.reading_1); }
			else if (reading.specification == 'Particle Size Distribution - PSD, D10 (µm)') { frappe.model.set_value(row.doctype, row.name, 'd10', reading.reading_1); }
			else if (reading.specification == 'Particle Size Distribution - PSD, D50 (µm)') { frappe.model.set_value(row.doctype, row.name, 'd50', reading.reading_1); }
			else if (reading.specification == 'Particle Size Distribution - PSD, D90 (µm)') { frappe.model.set_value(row.doctype, row.name, 'd90', reading.reading_1); }
			else if (reading.specification == 'Oxygen Content - O (wt%)') { frappe.model.set_value(row.doctype, row.name, 'o_wt', reading.reading_1); }
		}
	}
}