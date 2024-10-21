// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Export Log', {
	onload: function(frm) {
		frm.get_field('logs').grid.cannot_add_rows = true;
	},
	refresh: frm => {
		if(frm.doc.status != 'Submitted' && !frm.doc.__unsaved){
			frm.add_custom_button(__("Submit Payment Entry"),
			function () {
					if(frm.doc.__unsaved){
						frappe.throw("Please first save the document")
					}
					frappe.call({
						method : "vesta_si_erpnext.vesta_si_erpnext.doctype.payment_export_log.payment_export_log.submit_all_payment_entry",
						args : {
							self : frm.doc
						}
					})
				},
			).addClass("btn btn-primary");;
		}
		frm.add_custom_button(__('Cancel Payment Entry'), () => {
			let selected_row = []
			frm.doc.logs.forEach(e => {
				if(e.__checked && e.status == "Submitted"){
					selected_row.push({"payment_entry" : e.payment_entry, "log_ref" : e.name})
				}
			});
			if (!selected_row.length){
				frappe.throw("Please select at least one row.")
			}
			let seconds_elapsed = 0
			selected_row.forEach(e=>{
				setup_progress_bar(selected_row, seconds_elapsed)
			})
			frm.call({
				method : "cancelled_payment_entry",
				args : {
					"pe" : selected_row,
					"pe_log" : frm.doc.name
				},
				callback:(e)=>{
					frm.refresh()
				}
			})
		})
	}
});

function setup_progress_bar(selected_row, seconds_elapsed) {
	if (selected_row.length < 5) return;

	let interval = setInterval(function () {
		seconds_elapsed += 2;
		frappe.show_progress(__("Cancellation of a Payment Entry"), seconds_elapsed, selected_row.length);
	}, 1);
}
