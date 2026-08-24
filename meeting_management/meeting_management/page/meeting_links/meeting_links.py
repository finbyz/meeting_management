
import frappe
@frappe.whitelist()
def get_meeting_links():

	current_user = frappe.session.user

	# Get users visible to current user
	allowed_users = frappe.get_list(
		"User",
		fields=["name", "full_name"]
	)

	allowed_user_map = {
		d.name: d.full_name for d in allowed_users
	}

	records = frappe.get_all(
		"User Appointment Availability",
		filters={
			"enable_scheduling": 1,
			"user": ["in", list(allowed_user_map.keys())]
		},
		fields=[
			"user",
			"slug"
		]
	)

	base_url = frappe.utils.get_url()

	data = []

	for row in records:

		data.append({
			"user": row.user,
			"full_name": allowed_user_map.get(row.user),
			"personal_meeting_link": f"{base_url}/schedule/in/{row.slug}"
		})

	return data