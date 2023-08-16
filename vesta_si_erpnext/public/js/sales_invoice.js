frappe.ui.form.on("Sales Invoice", {
    refresh:function(frm){
        frm.add_custom_button(__('Stock Entry'), function (frm) {
                var d = new frappe.ui.Dialog({
                    title: __("Select Stock Entry"),
                    fields: [
                        {
                            'fieldname': 'Stock Entry',
                            'fieldtype': 'Link',
                            'label': __('Stock Entry'),
                            'options': 'Stock Entry',
                            "get_query": function () {
                                return {
                                    filters: [
                                        ["Stock Entry", "stock_entry_type", "=", "Manufacture"]
                                    ]
                                };
                            },
                            'reqd': 1
                        }
                    ],
                });
                d.set_primary_action(__('Get Items'), function(frm) {
                    d.hide();
                    var se = d.get_values();
                    frappe.call({                                  
                        method: "vesta_si_erpnext.vesta_si_erpnext.doc_events.sales_invoice.get_items_from_stock_entry",
                        args:{
                            stock_entry : se,
                        },
                        callback: function (r) {
                            if (r.message) {
                                if(cur_frm.doc.__islocal) {
                                    cur_frm.doc.items = []
                                }
                                r.message.forEach(d => {
                                    var c = cur_frm.add_child("items");
                                    c.item_code = d.item_code;
                                    c.item_name = d.item_name;
                                    c.rate = d.rate;
                                    c.qty = d.qty;
                                    c.uom = d.uom;
                                    c.description = d.description;
                                    c.batch_no = d.batch_no;
                                    c.warehouse = d.warehouse;
                                    c.stock_entry_detail = d.stock_entry_detail;
                                    cur_frm.refresh_field("items")
                                });
                            }
                        }
                    });
                });
                d.show();
            
        }, __('Get Items From'));
    }
})