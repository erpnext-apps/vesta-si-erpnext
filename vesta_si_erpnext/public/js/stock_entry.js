frappe.ui.form.on("Stock Entry", {
	setup_quality_inspection: function(frm) {
		if (!frm.doc.inspection_required) {
			frappe.msgprint({message: _("Please enable 'Inspection Required'."), title:_("Note")});
			return;
		}

		let quality_inspection_field = frm.get_docfield("items", "quality_inspection");
		quality_inspection_field.get_route_options_for_new_doc = function(row) {
			if (frm.is_new()) return;
			return {
				"inspection_type": "Incoming",
				"reference_type": frm.doc.doctype,
				"reference_name": frm.doc.name,
				"item_code": row.doc.item_code,
				"description": row.doc.description,
				"item_serial_no": row.doc.serial_no ? row.doc.serial_no.split("\n")[0] : null,
				"batch_no": row.doc.batch_no
			}
		}

		frm.set_query("quality_inspection", "items", function(doc, cdt, cdn) {
			return {
				filters: {
					docstatus: 1,
					reference_name: doc.name
				}
			}
		});
	},
});

frappe.ui.form.on("Stock Entry Detail", {
	quality_inspection: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		if (row.quality_inspection) {
			frappe.db.get_value("Quality Inspection", row.quality_inspection, "docstatus").then((r) => {
				if (cint(r.message.docstatus) == 0) {
					frappe.throw(__("Row #{0}: Please submit Quality Inspection {1}.",
						[row.idx, row.quality_inspection.bold()]))
				} else {
					frappe.db.get_list("Quality Inspection", {
						filters: { "name": ["=", row.quality_inspection]},
						fields: ["item_code", "analysed_item_code"]
					}).then((data) => {
						data = data[0];
						if (data.item_code === data.analysed_item_code && data.item_code !== row.item_code &&
								row.t_warehouse) {
							frappe.model.set_value(cdt, cdn, {
								"item_code": data.item_code,
								"is_scrap_item": 1,
								"is_finished_item": 0,
								"bom_no": ""
							});

							frm.get_field("items").grid.refresh();
						}
					});
				}
			});
		}
	},
});