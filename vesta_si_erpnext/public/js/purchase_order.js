frappe.ui.form.on("Purchase Order", {
    onload:function(frm){
        if (frm.doc.docstatus == 1 && !frappe.user.has_role("Over Billing Approver")){
            frm.remove_custom_button(__("Update Items"));
        }
    },
    refresh:function(frm){
        erpnext.utils.update_child_items = function(opts) {
            console.log("Hello")
            if (opts.frm.doc.docstatus == 1 && !frappe.user.has_role("Over Billing Approver")){
                frappe.throw("Insufficient permission for this operation")
            }
            const frm = opts.frm;
            const cannot_add_row = (typeof opts.cannot_add_row === 'undefined') ? true : opts.cannot_add_row;
            const child_docname = (typeof opts.cannot_add_row === 'undefined') ? "items" : opts.child_docname;
            const child_meta = frappe.get_meta(`${frm.doc.doctype} Item`);
            const get_precision = (fieldname) => child_meta.fields.find(f => f.fieldname == fieldname).precision;

            this.data = frm.doc[opts.child_docname].map((d) => {
                return {
                    "docname": d.name,
                    "name": d.name,
                    "item_code": d.item_code,
                    "delivery_date": d.delivery_date,
                    "schedule_date": d.schedule_date,
                    "conversion_factor": d.conversion_factor,
                    "qty": d.qty,
                    "rate": d.rate,
                    "uom": d.uom,
                    "item_tax_template": d.item_tax_template
                }
            });

            const fields = [{
                fieldtype:'Data',
                fieldname:"docname",
                read_only: 1,
                hidden: 1,
            }, {
                fieldtype:'Link',
                fieldname:"item_code",
                options: 'Item',
                in_list_view: 1,
                read_only: 0,
                disabled: 0,
                label: __('Item Code'),
                get_query: function() {
                    let filters;
                    if (frm.doc.doctype == 'Sales Order') {
                        filters = {"is_sales_item": 1};
                    } else if (frm.doc.doctype == 'Purchase Order') {
                        if (frm.doc.is_subcontracted) {
                            if (frm.doc.is_old_subcontracting_flow) {
                                filters = {"is_sub_contracted_item": 1};
                            } else {
                                filters = {"is_stock_item": 0};
                            }
                        } else {
                            return {
                                query: "vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_order.item_query",
                                filters: filters
                            };
                        }
                    }
                    return {
                        query: "erpnext.controllers.queries.item_query",
                        filters: filters
                    };
                }
            }, 
            {
                fieldtype:'Float',
                fieldname:"qty",
                default: 0,
                in_list_view: 1,
                read_only: 0,
                label: __('Qty'),
                precision: get_precision("qty")
            },
            {
                fieldtype:'Currency',
                fieldname:"rate",
                options: "currency",
                default: 0,
                read_only: 0,
                in_list_view: 1,
                label: __('Rate'),
                precision: get_precision("rate")
            },{
                fieldtype:'Link',
                fieldname:'uom',
                options: 'UOM',
                read_only: 0,
                label: __('UOM'),
                reqd: 1,
                onchange: function () {
                    frappe.call({
                        method: "erpnext.stock.get_item_details.get_conversion_factor",
                        args: { item_code: this.doc.item_code, uom: this.value },
                        callback: r => {
                            if(!r.exc) {
                                if (this.doc.conversion_factor == r.message.conversion_factor) return;

                                const docname = this.doc.docname;
                                dialog.fields_dict.trans_items.df.data.some(doc => {
                                    if (doc.docname == docname) {
                                        doc.conversion_factor = r.message.conversion_factor;
                                        dialog.fields_dict.trans_items.grid.refresh();
                                        return true;
                                    }
                                })
                            }
                        }
                    });
                }
            },  ];

            if (frm.doc.doctype == "Purchase Order"){
                fields.splice(4, 0, {
                    fieldtype: 'Link',
                    fieldname: "item_tax_template",
                    options:"Item Tax Template",
                    in_list_view: 1,
                    disabled:0,
                    label: __("Item Tax Template"),
                    get_query: function(e) {
                        let filters;
                        if(!e.item_code) {
                            return frm.doc.company ? {filters: {company: frm.doc.company}} : {};
                        } else {
                            filters = {
                                'item_code': e.item_code,
                                'valid_from': ["<=", frm.doc.transaction_date || frm.doc.bill_date || frm.doc.posting_date],
                            }
                            if (frm.doc.tax_category)
                                filters['tax_category'] = frm.doc.tax_category;
                            if (frm.doc.company)
                                filters['company'] = frm.doc.company;
                            
                            return {
                                query: "vesta_si_erpnext.api.get_tax_template",
                                filters: filters
                            }
                        }
                    }
                })
            }

            if (frm.doc.doctype == 'Sales Order' || frm.doc.doctype == 'Purchase Order' ) {
                fields.splice(2, 0, {
                    fieldtype: 'Date',
                    fieldname: frm.doc.doctype == 'Sales Order' ? "delivery_date" : "schedule_date",
                    in_list_view: 1,
                    label: frm.doc.doctype == 'Sales Order' ? __("Delivery Date") : __("Reqd by date"),
                    reqd: 1
                })
                fields.splice(7, 0, {
                    fieldtype: 'Float',
                    fieldname: "conversion_factor",
                    label: __("Conversion Factor"),
                    in_list_view: 1,
                    precision: get_precision('conversion_factor')
                })
            }

            frappe.call({
                method : "vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_order.remove_items_",
                args:{
                    items : this.data
                },
                callback:(r)=>{
                    this.data = r.message
                    new frappe.ui.Dialog({
                        title: __("Update Items"),
                        fields: [
                            {
                                fieldname: "trans_items",
                                fieldtype: "Table",
                                label: "Items",
                                cannot_add_rows: cannot_add_row,
                                in_place_edit: false,
                                reqd: 1,
                                data: this.data,
                                size: "extra-large", // small, large, extra-large 
                                get_data: () => {
                                    return this.data;
                                },
                                fields: fields,
                            },
                        ],
                        primary_action: function() {
                            const trans_items = this.get_values()["trans_items"].filter((item) => !!item.item_code);
                            frappe.call({
                                method: 'erpnext.controllers.accounts_controller.update_child_qty_rate',
                                freeze: true,
                                args: {
                                    'parent_doctype': frm.doc.doctype,
                                    'trans_items': trans_items,
                                    'parent_doctype_name': frm.doc.name,
                                    'child_docname': child_docname
                                },
                                callback: function() {
                                    frm.reload_doc();
                                }
                            });
                            this.hide();
                            refresh_field("items");
                        },
                        primary_action_label: __('Update')
                    }).show();
                }
            })
        }
        if (frm.doc.docstatus == 1 && !frappe.user.has_role("Over Billing Approver")){
            frm.remove_custom_button(__("Update Items"));
        }
    }
})

