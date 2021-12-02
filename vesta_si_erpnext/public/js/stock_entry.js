frappe.ui.form.on("Stock Entry", {
	setup: function(frm) {
		frm.set_indicator_formatter("item_code",
			function(doc) {
				if (doc.analysis_required) {
					return "yellow";
				} else if (!doc.s_warehouse) {
					return "blue";
				} else {
					return (doc.qty<=doc.actual_qty) ? "green" : "orange";
				}
			});
	},

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
				"batch_no": row.doc.batch_no,
				"rm_quality_inspection": row.doc.rm_quality_inspection
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
	batch_no(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (!row.is_finished_item) {
			frappe.db
				.get_list("Quality Inspection", {
					filters: {"batch_no": row.batch_no},
					fields: ["name"],
					order_by: "creation desc",
					limit: 1,
				})
				.then((res) => {
					console.log(res.length)
					if (!res.length) {
						row.quality_inspection = "";
					}
					else {
						row.quality_inspection = res[0].name;
					}
					frm.refresh_fields("items");
				})
		}
	},
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
			frappe.db.get_value("Work Order", frm.doc.work_order, "is_outpacking_wo").then((r) => {
				if (row.is_finished_item && row.t_warehouse) {
					frm.doc.items.slice(row.idx, frm.doc.items.length).forEach(f => {
						if (!row.quality_inspection) {
							frappe.model.set_value(f.doctype, f.name, 'quality_inspection', row.quality_inspection);
						}
					});
				}
			});
		}
	},
});