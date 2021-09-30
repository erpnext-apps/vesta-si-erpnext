from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():

    qi_template_fields = [
		dict(fieldname='item_name', label='Item', fieldtype='Link',
			insert_after='quality_inspection_template_name', options='Item')
	]
    qi_reading_fields = [
		dict(fieldname='frequency', label='Frequency', fieldtype='Int',
			insert_after='specification', hidden = 1)
	]
    iqip_fields = [
		dict(fieldname='frequency', label='Frequency', fieldtype='Int',
			insert_after='specification', in_list_view = 1)
	]

    custom_fields = {
		"Quality Inspection Template": qi_template_fields,
        "Quality Inspection Reading": qi_reading_fields,
        "Item Quality Inspection Parameter": iqip_fields
	}
    create_custom_fields(custom_fields, update=True)

