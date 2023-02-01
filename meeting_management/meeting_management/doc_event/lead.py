import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import now_datetime, nowdate

@frappe.whitelist()
def make_meetings(source_name, doctype, ref_doctype, target_doc=None):
	def set_missing_values(source, target):
		target.party_type = doctype
		target.party = source_name
		now = now_datetime()
		if ref_doctype == "Meeting Schedule":
			target.scheduled_from = target.scheduled_to = now
		else:
			target.meeting_from = target.meeting_to = now
			if doctype == "Lead":
				target.organization = source.company_name

	def update_contact(source, target, source_parent):
		pass

	doclist = get_mapped_doc(doctype, source_name, {
			doctype: {
				"doctype": ref_doctype,
				"field_map":  {
					'company_name': 'organisation',
					'customer_name':'organization',
					'contact_email':'email_id',
					'contact_mobile':'mobile_no',
					'organisation':'company_name',
				},
				"field_no_map": [
					"naming_series",
					"lead",
					"customer",
					"opportunity"
				],
				"postprocess": update_contact
			}
		}, target_doc, set_missing_values)

	return doclist
	