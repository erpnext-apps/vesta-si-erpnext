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
						for (let reading of readings) {
							if (reading.specification == 'Iron Content') { frappe.model.set_value(row.doctype, row.name, 'fe_wt', reading.reading_1); }
							else if (reading.specification == 'Calcium Content') { frappe.model.set_value(row.doctype, row.name, 'ca_wt', reading.reading_1); }
							else if (reading.specification == 'Aluminium Content') { frappe.model.set_value(row.doctype, row.name, 'al_wt', reading.reading_1); }
							else if (reading.specification == 'Carbon Content') { frappe.model.set_value(row.doctype, row.name, 'c_wt', reading.reading_1); }
							else if (reading.specification == 'D10 (Microns)') { frappe.model.set_value(row.doctype, row.name, 'd10', reading.reading_1); }
							else if (reading.specification == 'D50 (Microns)') { frappe.model.set_value(row.doctype, row.name, 'd50', reading.reading_1); }
							else if (reading.specification == 'D90 (Microns)') { frappe.model.set_value(row.doctype, row.name, 'd90', reading.reading_1); }
						}
					}
				}
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
						for (let reading of readings) {
							if (reading.specification == 'O2 Content') { frappe.model.set_value(row.doctype, row.name, 'o_wt', reading.reading_1); }
						}
					}
				}
			});
		}
	}
});