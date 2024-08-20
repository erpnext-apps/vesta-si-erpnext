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
	}
});
