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
let item_dict = [];
frappe.query_reports["Batch-Wise Balance and Inspection"] = {
	"filters": filters,
	get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true,
			events: {
				onCheckRow: function(data) {
					console.log('adding now')
					item_dict.push({
						"item_code" : data[2].content,
						"batch_no" : data[5].content,
						"warehouse" : data[4].content,
						"qty": data[6].content,
						"uom": data[7].content,
						"qi": data[8].content
					})				
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
		item_dict = []

	}
}
