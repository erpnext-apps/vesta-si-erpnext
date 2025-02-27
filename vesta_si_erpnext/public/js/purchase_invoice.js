frappe.ui.form.on("Purchase Invoice", {
    setup:()=>{
    },
    onload:(frm)=>{
        frm.doc.items.forEach(element => {
            if (element.purchase_receipt){
                console.log("HHHH")
                cur_frm.get_field("items").grid.wrapper.find(".grid-add-multiple-rows").addClass("hidden");
                frm.get_field('items').grid.cannot_add_rows = true;
            }
        });
    },
    refresh:function(frm){
        frm.trigger("add_unreconcile_btn")
        frm.doc.items.forEach(element => {
            if (element.purchase_receipt){
                console.log("HHHH")
                frm.get_field('items').grid.cannot_add_rows = true;
                cur_frm.get_field("items").grid.wrapper.find(".grid-add-multiple-rows").addClass("hidden");
                document.querySelectorAll(".grid-add-multiple-rows").forEach(el => el.classList.add("hidden"));

            }
        });
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