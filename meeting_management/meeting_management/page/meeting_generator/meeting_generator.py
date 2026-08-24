import frappe
from frappe.utils import get_url
from frappe import _
@frappe.whitelist()
def get_simple_user_list():
    """Returns users who have an active availability record."""
    available_users = frappe.get_all(
        "User Appointment Availability",
        filters={"enable_scheduling": 1},
        pluck="user"
    )

    if not available_users:
        return []

    return frappe.get_all(
        "User",
        filters={"name": ["in", available_users]},
        fields=["name", "full_name"]
    )

@frappe.whitelist()
def get_user_scheduler_url(user: str) -> str:
    """Generates the direct URL for a specific user's scheduler."""
    avail_records = frappe.get_all(
        "User Appointment Availability",
        filters={"user": user, "enable_scheduling": 1},
        fields=["name", "slug"]
    )

    if not avail_records:
        frappe.throw(_("No active availability found for this user."))

    avail = avail_records[0]

    durations = frappe.get_all(
        "Appointment Slot Duration",
        filters={"parent": avail.name},
        fields=["name"]
    )

    if not durations:
        frappe.throw(_("No slot durations defined for this user."))

    base_url = get_url(f"/schedule/in/{avail.slug}")
    return f"{base_url}?type={durations[0].name}"