frappe.ui.form.on("Purchase Receipt", {
    refresh:function(frm){
        cur_frm.get_field("items").grid.wrapper.find(".grid-add-multiple-rows").addClass("hidden");
        frm.get_field('items').grid.cannot_add_rows = true;
    }
})