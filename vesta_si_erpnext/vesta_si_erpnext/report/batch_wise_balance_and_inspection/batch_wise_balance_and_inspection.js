// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
let filters = [
	{
		"fieldname":"company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"default": frappe.defaults.get_user_default("Company"),
		"reqd": 1
	},
	{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Date",
		"width": "80",
		"default": frappe.sys_defaults.year_start_date,
		"reqd": 1
	},
	{
		"fieldname":"to_date",
		"label": __("To Date"),
		"fieldtype": "Date",
		"width": "80",
		"default": frappe.datetime.get_today(),
		"reqd": 1
	},
	{
		"fieldname":"item_code",
		"label": __("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"get_query": function() {
			return {
				filters: {
					"has_batch_no": 1
				}
			};
		}
	},
	{
		"fieldname":"warehouse",
		"label": __("Warehouse"),
		"fieldtype": "Link",
		"options": "Warehouse",
		"get_query": function() {
			let company = frappe.query_report.get_filter_value('company');
			return {
				filters: {
					"company": company
				}
			};
		}
	},
	{
		"fieldname":"batch_no",
		"label": __("Batch No"),
		"fieldtype": "Link",
		"options": "Batch",
		"get_query": function() {
			let item_code = frappe.query_report.get_filter_value('item_code');
			return {
				filters: {
					"item": item_code
				}
			};
		}
	},
	{
		"fieldname":"quality_inspection",
		"label": __("Quality Inspection"),
		"fieldtype": "Link",
		"options": "Quality Inspection",
		"get_query": function() {
			return {
				filters: {
					"docstatus": 1
				}
			};
		}
	},
	{
		"fieldname":"supplier_bag_no",
		"label": __("Supplier Bag No."),
		"fieldtype": "Data",
	},
];
frappe.xcall(
	'vesta_si_erpnext.vesta_si_erpnext.report.batch_wise_balance_and_inspection.batch_wise_balance_and_inspection.get_params'
	).then((data) => {
		for (d in data) {
			filters.push({
				"fieldname":data[d]['col_name'],
				"label": __(data[d]['inspection_parameter']),
				"fieldtype": "Data",
			});
		}
	})
let item_dict = {};
frappe.query_reports["Batch-Wise Balance and Inspection"] = {
	"filters": filters,
	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
			events: {
				onCheckRow: function(data) {
					item_dict = {};
					let indexes = frappe.query_report.datatable.rowmanager.getCheckedRows();

					if (indexes && indexes.length) {
						const items = indexes.map(i => frappe.query_report.data[i]).filter(i => i != undefined);
						if (items && items.length) {
							items.forEach(d => {
								key = d.item + d.warehouse + d.batch
								item_dict[key] = {
									"item_code" : d.item,
									"batch_no" : d.batch,
									"warehouse" : d.warehouse,
									"qty": d.balance_qty,
									"uom": d.uom,
									"stock_uom": d.uom,
									"quality_inspection": d.quality_inspection,
								}
							});
						}
					}
				},
			}
		});
	},
	"formatter": function (value, row, column, data, default_formatter) {
		if (column.fieldname == "Batch" && data && !!data["Batch"]) {
			value = data["Batch"];
			column.link_onclick = "frappe.query_reports['Batch-Wise Balance and Inspection'].set_batch_route_to_stock_ledger(" + JSON.stringify(data) + ")";
		}

		value = default_formatter(value, row, column, data);
		return value;
	},
	"set_batch_route_to_stock_ledger": function (data) {
		frappe.route_options = {
			"batch_no": data["Batch"]
		};

		frappe.set_route("query-report", "Stock Ledger");


    },

    onload: function(report) {
		// create SE
        report.page.add_inner_button(__("Create Stock Entry"), function() {
		if (item_dict.length == 0)
			frappe.throw("Select atleast 1 row to create a Stock Entry!")
		frappe.xcall(
		'vesta_si_erpnext.vesta_si_erpnext.report.batch_wise_balance_and_inspection.batch_wise_balance_and_inspection.create_stock_entry', {
			item_list: item_dict,
			}).then(stock_entry => {
			frappe.model.sync(stock_entry);
			frappe.set_route("Form", 'Stock Entry', stock_entry.name);
			});
		})

		// create certificate
		report.page.add_inner_button(__("Create Certificate"), function() {
			if (item_dict.length == 0)
				frappe.throw("Select atleast 1 row to create a Certificate!")

			frappe.xcall(
			'vesta_si_erpnext.vesta_si_erpnext.report.batch_wise_balance_and_inspection.batch_wise_balance_and_inspection.create_certificate', {
				item_list: item_dict,
				}).then(analytical_certificate => {
				frappe.model.sync(analytical_certificate);
				frappe.set_route("Form", 'Analytical Certificate Creation', analytical_certificate.name);
				});
			})

	}
}
