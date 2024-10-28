// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Export Log', {
	onload: function(frm) {
		frm.get_field('logs').grid.cannot_delete_rows = true;
		frm.get_field('logs').grid.cannot_delete_all_rows = true;
		frm.get_field('logs').grid.cannot_add_rows = true;

	},
	refresh: frm => {
		frm.get_field('logs').grid.cannot_delete_rows = true;
		frm.get_field('logs').grid.cannot_delete_all_rows = true;
		frm.get_field('logs').grid.cannot_add_rows = true;
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
			let msg = '<ul>'
			frm.doc.logs.forEach(e => {
				if(e.__checked && e.status == "Submitted"){
					selected_row.push({"payment_entry" : e.payment_entry, "log_ref" : e.name})
					msg += `<li>${e.payment_entry}</li>`
				}
			});
			msg += '</ul><br><p>Would you like to cancel the Selected Payment entry?</p>'
			if (!selected_row.length){
				frappe.throw("Please select at least one row of submitted payment entry.")
			}
			let seconds_elapsed = 0
			
			frappe.warn(`Are you sure you want to proceed to cancelled selected ${selected_row.length} Payment Entry?`,
				msg,
				() => {
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
							frm.refresh_field("logs")
							cur_frm.refresh()
						}
					})
				},
				'Continue',
				true // Sets dialog as minimizable
			)
			
		}).addClass("btn btn-primary")
	}
});

function setup_progress_bar(selected_row, seconds_elapsed) {
	if (selected_row.length < 5) return;

	let interval = setInterval(function () {
		seconds_elapsed += 2;
		frappe.show_progress(__("Cancellation of a Payment Entry"), seconds_elapsed, selected_row.length);
	}, 1);
}
