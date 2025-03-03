frappe.ui.form.on("Purchase Invoice", {

    refresh:function(frm){
        frm.trigger("add_unreconcile_btn")
    },
    add_unreconcile_btn:function(frm) {
		if (frm.doc.docstatus == 0 && !frm.is_new()) {
            frm.add_custom_button(
                __("UnReconcile"),
                function () {
                    frappe.call({
                        method: "vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_invoice.check_any_advance_payment",
                        args: {
                            self : frm.doc,
                        },
                        callback:(r)=>{
                            if (r.message){
                                let frm = { "doc" : r.message}
                                erpnext.accounts.unreconcile_payment.build_unreconcile_dialog(frm);
                            }
                        }
                    })
                },
                __("Actions")
            );
		}
	},
})