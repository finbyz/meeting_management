import frappe

@frappe.whitelist()
def get_dashboard_data():
	# 1. Number cards stats
	total_tasks = frappe.db.count("SNM Task", filters={"status": ["!=", "Completed"]})
	overdue_tasks = frappe.db.count("SNM Task", filters={"status": "Overdue"})
	working_tasks = frappe.db.count("SNM Task", filters={"status": "Working"})
	completed_tasks = frappe.db.count("SNM Task", filters={"status": "Completed"})
	all_tasks = frappe.db.count("SNM Task")
	total_events = frappe.db.count("Event")

	# 2. Get task list details (limit to 100 for performance, can search/filter client side)
	tasks = frappe.get_all(
		"SNM Task",
		fields=["name", "subject", "status", "priority", "due_date", "creation"],
		limit=100,
		order_by="creation desc"
	)

	# 3. Get event list details
	events = frappe.get_all(
		"Event",
		fields=["name", "subject", "starts_on", "ends_on", "creation"],
		limit=100,
		order_by="starts_on desc"
	)

	# 4. Chart 1: Group by status (Open Tasks x Total Tasks)
	status_chart_data = frappe.db.sql(
		"select status, count(name) as count from `tabSNM Task` group by status",
		as_dict=True
	)

	# Chart 2: Group by priority (Task Priorities)
	priority_chart_data = frappe.db.sql(
		"select priority, count(name) as count from `tabSNM Task` group by priority",
		as_dict=True
	)

	return {
		"stats": {
			"total_tasks": total_tasks,
			"overdue_tasks": overdue_tasks,
			"working_tasks": working_tasks,
			"completed_tasks": completed_tasks,
			"total_events": total_events,
			"all_tasks": all_tasks
		},
		"tasks": tasks,
		"events": events,
		"status_chart": status_chart_data,
		"priority_chart": priority_chart_data
	}
