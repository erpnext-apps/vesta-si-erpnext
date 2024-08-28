frappe.ui.form.on("Item", {
    is_fixed_asset:function(frm){
        cur_frm.fields_dict['asset_category'].get_query = function(doc) {
            // filter on Account
            return {
                filters: {
                   "custom_disabled":0
                }
            }
        }
    }
})