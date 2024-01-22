frappe.pages['payment-export'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Payment Export',
		single_column: true
	});
	frappe.payment_export.make(page);
    page.payment_export_settings_field = page.add_field({
        fieldname: 'payment_export_settings',
		label: __('Payment Export Settings'),
		fieldtype:'Link',
		options:'Payment Export Settings',
        default:"PES0001"
	});
    page.posting_date_field = page.add_field({
        fieldname: 'posting_date',
		label: __('Required Execution Date'),
		fieldtype:'Date',
        default:"Today"
	});
    page.payment_type_field = page.add_field({
        fieldname: 'payment_type',
		label: __('Payment Type'),
		fieldtype:'Select',
        default:"Domestic (Swedish) Payments",
        options:"Domestic (Swedish) Payments\nSEPA\nCross Border Payments",
        onchange: () => {
            frappe.payment_export.run(page);
	    getfindSelected()
        }
	});
    frappe.payment_export.run(page);
    getfindSelected()
}

frappe.payment_export = {
	start: 0,
	make: function(page) {
		var me = frappe.payment_export;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		var data = "";
		$(frappe.render_template('payment_export', data)).appendTo(me.body);

		// attach button handlers
		this.page.main.find(".btn-create-file").on('click', function() {
			var me = frappe.payment_export;
			
            // find selected payments
            var checkedPayments = findSelected();
            if (checkedPayments.length > 0) {
                var payments = [];
                for (var i = 0; i < checkedPayments.length; i++) {
                    payments.push(checkedPayments[i].name);
                }
                
                // generate payment file
                frappe.call({
                    method: 'vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export.generate_payment_file',
                    args: { 
                        'payments': payments,
                        "payment_export_settings": page.payment_export_settings_field.get_value(),
                        "posting_date": page.posting_date_field.get_value(),
                        'payment_type':page.payment_type_field.get_value()
                       
                    },
                    callback: function(r) {
                        if (r.message) {
                            // log errors if present
                            var parent = page.main.find(".insert-log-messages").empty();
                            if (r.message.skipped.length > 0) {
                                $('<p>' + __("Some payments were skipped due to errors (check the payment file for details): ") + '</p>').appendTo(parent);
                                for (var i = 0; i < r.message.skipped.length; i++) {
									$('<p><a href="/desk/Form/Payment Entry/'
									  + r.message.skipped[i] + '">' 
									  + r.message.skipped[i] + '</a></p>').appendTo(parent);
								}
                            }
                            else {
                                $('<p>' + __("No errors") + '</p>').appendTo(parent);
                            }

                            // prepare the xml file for download
                            download("payments.xml", r.message.content);
                            
                            // remove create file button to prevent double payments
                            page.main.find(".btn-create-file").addClass("hide");
                            page.main.find(".btn-refresh").removeClass("hide");
                        } 
                    }
                });
                
            } else {
                frappe.msgprint( __("Please select at least one payment."), __("Information") );
            }
		});
        this.page.main.find(".btn-refresh").on('click', function() {
            // refresh
            location.reload(); 
        });
	},
	run: function(page) {  
		// populate payment entries
		frappe.call({
			method: 'vesta_si_erpnext.vesta_si_erpnext.page.payment_export.payment_export.get_payments',
			args: { 
                'payment_type':page.payment_type_field.get_value()
             },
			callback: function(r) {
				if (r.message) {
					var parent = page.main.find(".payment-table").empty();
                    if (r.message.payments.length > 0) {
                        $(frappe.render_template('payment_export_table', r.message)).appendTo(parent);
                    } else {
                        $('<p class="text-muted">' + __("No payment entries to be paid found with status draft") + '</p>').appendTo(parent);
                    }
				} 
			}
		});
	}
}

function download(filename, content) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:application/octet-stream;charset=utf-8,' + encodeURIComponent(content));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function findSelected() {
    var inputs = document.getElementsByTagName("input"); 
    var checkboxes = []; 
    var checked = []; 
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == "checkbox" && inputs[i].classList.contains("inputcheck")) {
        checkboxes.push(inputs[i]);
        if (inputs[i].checked) {
          checked.push(inputs[i]);
        }
      }
    }
    return checked;
}
function getfindSelected() {
    
    var inputs = document.getElementsByTagName("input"); 
    var checked = []; 
    var a = 0
    for (var i = 0; i < inputs.length; i++) {

        if (inputs[i].classList.contains("inputcheck")) {
            checked.push(inputs[i])
          var isChecked = inputs[i].checked;

          if (isChecked) {
            a++;
          }
        }
      }
    if(checked.length || a){
        document.getElementById("update_selected").innerText = `${a}/${checked.length} Selected` 
    }
    
}
function selectunselect(){
    
    var inputCheck = document.querySelector('.selectall');
    var indexerCheckboxes = document.querySelectorAll('.inputcheck');

    
    indexerCheckboxes.forEach(function(indexerCheckbox) {
        indexerCheckbox.checked = inputCheck.checked;
    });
    
    getfindSelected()
}
