frappe.ui.form.on('Quality Inspection Parameter', {
    onload: function(frm) {
		
		frappe.model.with_doctype("Analytical Certificate Drum", () => {
			var fields = $.map(frappe.get_doc("DocType", "Analytical Certificate Drum").fields, function(d) {
				if (frappe.model.no_value_type.indexOf(d.fieldtype) === -1 || ['Button'].includes(d.fieldtype)) {
					return { label: d.label , value: d.fieldname };
				} else {
					return null;
				}
			});
			
			frm.set_df_property("certificate_parameter_column", "options", fields);
			frm.refresh_field("certificate_parameter_column");
			
			
		});
	},
    certificate_parameter_column: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		var df = $.map(frappe.get_doc("DocType", "Analytical Certificate Drum").fields, function(d) {
			return doc.certificate_parameter_column == d.fieldname ? d : null;
		})[0];
		doc.certificate_column_name = df.fieldname
		frm.refresh_field("certificate_column_name");
	},
})