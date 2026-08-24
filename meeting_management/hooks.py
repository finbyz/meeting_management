# Copyright (c) 2023, Finbyz Tech PVT LTD and contributors
# For license information, please see license.txt

from . import __version__ as app_version

app_name = "meeting_management"
app_title = "Meeting Management"
app_publisher = "Finbyz Tech PVT LTD"
app_description = "meeting"
app_email = "info@finbyz.tech"
app_license = "MIT"

# Includes in <head>
# -----------------
# -
fixtures=[
     {
    "doctype": "Notification",
        "filters": [
            [
                "name", "in", [
                    "Meeting"
                ]
            ]
        ]

},
{
    "doctype": "Server Script",
        "filters": [
            [
                "name", "in", [
                    "SNM Task"
                ]
            ]
        ]

},
# {
#     "doctype": "Kanban Board",
#         "filters": [
#             [
#                 "name", "in", [
#                     "All Task","My Task"
#                 ]
#             ]
#         ]

# },
]

after_migrate = "meeting_management.migrate.after_migrate"

# include js, css files in header of desk.html
# app_include_css = "/assets/meeting_management/css/meeting_management.css"
app_include_js = "/assets/meeting_management/js/kanban_filter.js"

# include js, css files in header of web template
# web_include_css = "/assets/meeting_management/css/meeting_management.css"
# web_include_js = "/assets/meeting_management/js/meeting_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "meeting_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Lead":"public/js/lead.js",
    "Customer":"public/js/customer.js",
    "Opportunity":"public/js/opportunity.js",
}
permission_query_conditions = {
	"Meeting": "meeting_management.meeting_management.doctype.meeting.meeting.get_permission_query_conditions"
}

has_permission = {
	"Meeting": "meeting_management.meeting_management.doctype.meeting.meeting.has_permission"
}
# doctype_js = {"doctype" : "public/js/doctype.js"}
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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "meeting_management.utils.jinja_methods",
#	"filters": "meeting_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "meeting_management.install.before_install"
# after_install = "meeting_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "meeting_management.uninstall.before_uninstall"
# after_uninstall = "meeting_management.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "meeting_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways



# DocType Class
# ---------------
# Override standard doctype classes
override_doctype_dashboards = {
	"Lead": "meeting_management.api.lead_get_data"
}
# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

doc_events = {
    "ToDo": {
        "after_insert": "meeting_management.meeting_management.doctype.snm_task.snm_task.update_snm_task_whatsapp_numbers_from_todo",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"meeting_management.meeting_management.doctype.snm_task.snm_task.send_overdue_task_notifications"
	]
}
# Testing
# -------

# before_tests = "meeting_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {customer_dashboard
#	"frappe.desk.doctype.event.event.get_events": "meeting_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "meeting_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"meeting_management.auth.validate"
# ]

override_whitelisted_methods = {
    "erpnext.selling.doctype.customer.customer_dashboard.get_data": "meeting_management.api.customer_get_data"
}
