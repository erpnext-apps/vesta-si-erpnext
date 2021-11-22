frappe.ui.form.off("Quality Inspection", "item_code");

frappe.ui.form.on("Quality Inspection", {
	setup: function(frm) {
		frm.set_indicator_formatter('analysis_item_code',
			function(doc) {
				return (doc.status && doc.status === "Accepted") ? "green" : "orange";
			});

		frm.set_query("item_code", {}); // unset item code query

		frm.set_query("analysed_item_code", () => {
			let accepted_items = frm.doc.inspection_summary_table.filter(
				d => d.status === "Accepted").map(d => d.analysis_item_code);

			return {
				filters : {
					name: ["in", accepted_items]
				}
			}
		});
	},

	item_code: function(frm) {
		if (frm.doc.item_code) {
			if (!frm.doc.analysed_item_code) {
				// if no analysed item code, overwrite tables, analysis isnt done
				frappe.call({
					method: "get_quality_inspection_template",
					doc: frm.doc,
					callback: function() {
						refresh_field(['quality_inspection_template', 'readings']);
						frm.events.auto_fill_inspection_summary(frm, true);
					}
				});
				if (frm.doc.rm_quality_inspection){
				frappe.db.get_doc('Quality Inspection', frm.doc.rm_quality_inspection).then(qi => {
					qi.readings.forEach((ref) => {
						frm.doc.readings.forEach((reading) => {
							if (ref.specification == reading.specification){
							frappe.model.set_value(reading.doctype, reading.name, 'reading_1', ref.reading_1);
							}
						});
					});
				});
			}
			} else {
				// if analysis is done, only overwrite template field and min/max values.
				// Dont touch input data and analysis summary
				frappe.db.get_value("Item", frm.doc.item_code, "quality_inspection_template").then((r) => {
					frm.doc.quality_inspection_template = r.message.quality_inspection_template;
					frm.refresh_field("quality_inspection_template");
					frappe.call({
						method: "vesta_si_erpnext.vesta_si_erpnext.quality_inspection.get_template_details",
						args : {
							template: r.message.quality_inspection_template
						},
						callback: function(res) {
							frm.doc.readings.forEach((row) => {
								let data = res.message[row.specification];
								row = Object.assign(row, data);
							})
							frm.get_field("readings").grid.refresh();
						}
					});
				});
			}
		}

	},

	quality_inspection_template: function(frm) {
		if (frm.doc.quality_inspection_template && !frm.doc.analysed_item_code) {
			frm.events.auto_fill_inspection_summary(frm, false);
		}
	},

	auto_fill_inspection_summary: function(frm, from_item=true) {
		frappe.call({
			method: "vesta_si_erpnext.vesta_si_erpnext.quality_inspection.fetch_analysis_priority_list",
			args: {
				item: from_item ? frm.doc.item_code : null,
				template: from_item ? null : frm.doc.quality_inspection_template
			},
			callback: function(result) {
				if (!result.exc && result.message) {
					frm.clear_table("inspection_summary_table");

					let priorities = result.message;
					priorities.forEach((row) => {
						let child = frm.add_child("inspection_summary_table");
						child.analysis_item_code = row.item_code;
						child.inspection_template = row.inspection_template;
					});

					frm.get_field("inspection_summary_table").grid.refresh();
				}
			}
		});
	},

	run_analysis: function(frm) {
		if (!frm.doc.inspection_summary_table || !frm.doc.inspection_summary_table.length) {
			frappe.throw("No Items to Analyse.")
		}

		frappe.call({
			method: "vesta_si_erpnext.vesta_si_erpnext.quality_inspection.run_analysis",
			args: {
				readings: frm.doc.readings,
				priority_list: frm.doc.inspection_summary_table
			},
			callback: function(result) {
				if (!result.exc && result.message) {
					frm.clear_table("inspection_summary_table");

					let summary = result.message;
					summary.forEach((row) => {
						let child = frm.add_child("inspection_summary_table");
						Object.assign(child, row);
					});

					frm.get_field("inspection_summary_table").grid.refresh();
				}
			}
		})
	},

	analysed_item_code: function(frm) {
		if (frm.doc.analysed_item_code) {
			frm.set_value("item_code", frm.doc.analysed_item_code);
		}
	}
})