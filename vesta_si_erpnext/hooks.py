# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "vesta_si_erpnext"
app_title = "Vesta Si Erpnext"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "A custom Frappe App for Vesta Si Sweden AB"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "developers@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vesta_si_erpnext/css/vesta_si_erpnext.css"
# app_include_js = "/assets/vesta_si_erpnext/js/vesta_si_erpnext.js"

# include js, css files in header of web template
# web_include_css = "/assets/vesta_si_erpnext/css/vesta_si_erpnext.css"
# web_include_js = "/assets/vesta_si_erpnext/js/vesta_si_erpnext.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vesta_si_erpnext/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Quality Inspection" : "public/js/quality_inspection.js",
	"Stock Entry": "public/js/stock_entry.js",
	"Quality Inspection Parameter": "public/js/quality_inspection_parameter.js",
	"Sales Invoice":"public/js/sales_invoice.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "vesta_si_erpnext.install.before_install"
# after_install = "vesta_si_erpnext.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vesta_si_erpnext.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

fixtures = ["Custom Field"]

doc_events = {
	"Quality Inspection Template": {
		"validate": "vesta_si_erpnext.vesta_si_erpnext.quality_inspection_template.validate"
	},
	"Quality Inspection": {
		"validate": "vesta_si_erpnext.vesta_si_erpnext.quality_inspection.validate_events",
		"on_submit": "vesta_si_erpnext.vesta_si_erpnext.quality_inspection.on_submit_events"
	},
	"Stock Entry": {
		"on_submit": "vesta_si_erpnext.vesta_si_erpnext.stock_entry.link_supplier_bag_to_batch",
		"before_validate": "vesta_si_erpnext.vesta_si_erpnext.stock_entry.before_validate_events",
		"before_submit": "vesta_si_erpnext.vesta_si_erpnext.stock_entry.before_submit_events",
		"validate": "vesta_si_erpnext.vesta_si_erpnext.stock_entry.set_quality_inspection",
		"on_update": "vesta_si_erpnext.vesta_si_erpnext.purchase_receipt.on_update"
	},
	"Purchase Receipt": {
		"on_submit": "vesta_si_erpnext.vesta_si_erpnext.purchase_receipt.link_supplier_bag_to_batch",
		"before_validate": "vesta_si_erpnext.vesta_si_erpnext.purchase_receipt.before_validate",
		"on_update": "vesta_si_erpnext.vesta_si_erpnext.purchase_receipt.on_update"
	},
	"Purchase Order":{
		"validate":"vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_order.validate"
	},
	"Payment Entry": {
		"validate": "vesta_si_erpnext.vesta_si_erpnext.doc_events.payment_entry.validate",
		"on_submit": "vesta_si_erpnext.vesta_si_erpnext.doc_events.payment_entry.on_submit"
	},
	"Purchase Invoice": {
		"on_update_after_submit": "vesta_si_erpnext.vesta_si_erpnext.doc_events.purchase_invoice.set_due_date_after_submit"
	},
	"GL Entry":{
		'validate': "vesta_si_erpnext.vesta_si_erpnext.doc_events.sales_invoice.check_account_frozzen_date",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vesta_si_erpnext.tasks.all"
# 	],
# 	"daily": [
# 		"vesta_si_erpnext.tasks.daily"
# 	],
# 	"hourly": [
# 		"vesta_si_erpnext.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vesta_si_erpnext.tasks.weekly"
# 	]
# 	"monthly": [
# 		"vesta_si_erpnext.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "vesta_si_erpnext.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.stock.doctype.putaway_rule.putaway_rule.apply_putaway_rule": "vesta_si_erpnext.vesta_si_erpnext.putaway_rule.apply_putaway_rule"
}

override_doctype_class = {
	"Stock Entry": "vesta_si_erpnext.vesta_si_erpnext.stock_entry.CustomStockEntry",
	"Purchase Invoice": "vesta_si_erpnext.overrides.purchase_invoice.CustomPurchaseInvoice"
	}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vesta_si_erpnext.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

