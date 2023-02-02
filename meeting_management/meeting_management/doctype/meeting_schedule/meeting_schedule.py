# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json, os, datetime
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import msgprint, db, _
from frappe.core.doctype.communication.email import make
from frappe.utils import get_datetime
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_contact_details, get_default_contact
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from frappe.email.smtp import SMTPServer
import smtplib
from frappe.utils.user import get_user_fullname
import re

class MeetingSchedule(Document):
	@frappe.whitelist()
	def send_invitation(self):	
		if not self.email_id:
			msgprint(_("Please enter email id"))
			return

		CRLF = "\r\n"
		default_sender_name, default_sender =frappe.db.get_value('Email Account',{'default_outgoing':1},['name','email_id'])
		if not default_sender:
			frappe.throw("Please Setup Default Outgoing Email Account.")
		organizer = "ORGANIZER;CN=" +default_sender+":mailto:"+default_sender
		dtstamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
		dtstart = get_datetime(self.scheduled_from).strftime("%Y%m%dT%H%M%S")
		dtend = get_datetime(self.scheduled_to).strftime("%Y%m%dT%H%M%S")
		attendees=[]
		if self.cc_to:
			cc = self.cc_to.replace(' ','')
			attendees = cc.split(',')
		attendees.append(self.email_id)
		subject = "Scheduled Meeting on %s " % get_datetime(self.scheduled_from).strftime("%A %d-%b-%Y")
		cleanr = re.compile('<.*?>')
		attendee = ""
		for att in attendees:
			attendee += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE"+CRLF+" ;CN="+att+";X-NUM-GUESTS=0:mailto:"+att+CRLF
		ical = "BEGIN:VCALENDAR"+CRLF+"""PRODID:-//Google Inc//Google Calendar 70.9054//EN"""+CRLF+"VERSION:2.0"+CRLF+"CALSCALE:GREGORIAN"+CRLF
		ical+="METHOD:REQUEST"+CRLF+"BEGIN:VEVENT"+CRLF+"DTSTART:"+dtstart+CRLF+"DTEND:"+dtend+CRLF+"DTSTAMP:"+dtstamp+CRLF+organizer+CRLF
		ical+= "UID:FIXMEUID"+dtstamp+CRLF
		ical+= attendee+"CREATED:"+dtstamp+CRLF
		# if self.invitation_message:
		# 	ical+= "DESCRIPTION:"+re.sub(cleanr, '', self.invitation_message) +CRLF
		ical+="LAST-MODIFIED:"+dtstamp+CRLF+"LOCATION:"+CRLF+"SEQUENCE:0"+CRLF+"STATUS:CONFIRMED"+CRLF
		ical+= "SUMMARY:"+subject+CRLF
		ical+="TRANSP:OPAQUE"+CRLF+"END:VEVENT"+CRLF+"END:VCALENDAR"+CRLF

		msg = MIMEMultipart('alternative')
		msg['Reply-To']=self.email_id
		msg['Date'] = formatdate(localtime=True)
		msg['Subject'] = subject
		msg['From'] = self.email_id
		msg['To'] = ",".join(attendees)
		msg.add_header('Content-class', 'urn:content-classes:calendarmessage')

		email_body = ""
		# part_email = MIMEText(ical,'calendar;method=REQUEST')
		if self.invitation_message:
			email_body = MIMEText(self.invitation_message, 'html')

		msg.attach(email_body)
		msgAlternative = MIMEMultipart('alternative')

		# ical_atch = MIMEBase('text/calendar',' ;name="%s"'%"invite.ics")
		ical_atch = MIMEBase('text', 'calendar', **{'method' : 'REQUEST', 'name' : 'invite.ics'})
		ical_atch.set_payload(ical)
		encoders.encode_base64(ical_atch)
		ical_atch.add_header('Content-class', 'urn:content-classes:calendarmessage')
		ical_atch.add_header('Content-Disposition', 'attachment; filename="%s"'%("invite.ics"))

		# msgAlternative.attach(part_email)
		msgAlternative.attach(ical_atch)
		msg.attach(msgAlternative)

		# Added to get Parameters which are used in SMTPserver Class
		from frappe.email.doctype.email_account.email_account import EmailAccount
		from frappe.utils.password import get_decrypted_password
		email_account = EmailAccount.find_outgoing(match_by_doctype=None)
		password = get_decrypted_password(email_account.doctype, email_account.name, "password")

		smtpserver = SMTPServer(server = email_account.smtp_server, login = email_account.email_id, password = password, service = email_account.service, port=email_account.smtp_port, use_ssl = email_account.use_ssl_for_outgoing, use_tls = email_account.use_tls)
		smtpserver.session.sendmail(default_sender, attendees, msg.as_string())

		doc = frappe.new_doc("Communication")
		doc.subject = subject
		doc.communication_medium = "Email"
		doc.sender = default_sender
		doc.recipients = self.email_id
		doc.cc = self.cc_to
		doc.content = self.invitation_message
		doc.communication_type = "Communication"
		doc.status="Linked"
		doc.sent_or_received = "Sent"
		doc.sender_full_name = get_user_fullname(frappe.session.user)
		doc.reference_doctype = self.doctype
		doc.reference_name = self.name
		doc.reference_owner = frappe.session.user
		doc.user = frappe.session.user
		doc.email_account = default_sender_name
		doc.save(ignore_permissions=True)

@frappe.whitelist()
def make_meeting(source_name, target_doc=None):	
	doclist = get_mapped_doc("Meeting Schedule", source_name, {
			"Meeting Schedule":{
				"doctype": "Meeting",
				"field_map": {
					"name": "schedule_ref",
					"scheduled_from": "meeting_from",
					"scheduled_to": "meeting_to",
				},
				"field_no_map": [
					"naming_series",
					"lead",
					"customer",
					"opportunity"
				]
			}
	}, target_doc)	
	return doclist
	
@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	filters = json.loads(filters)
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Meeting Schedule", filters)

	data = frappe.db.sql("""
			select 
				name, scheduled_from, scheduled_to, organisation
			from 
				`tabMeeting Schedule`
			where
				(scheduled_from <= %(end)s and scheduled_to >= %(start)s) {conditions}
			""".format(conditions=conditions),
				{
					"start": start,
					"end": end
				}, as_dict=True, update={"allDay": 0})

	if not data:
		return []
		
	data = [x.name for x in data]

	return frappe.db.get_list("Meeting Schedule",
		{ "name": ("in", data), "docstatus":1},
		["name", "scheduled_from", "scheduled_to", "organization"]
	)			

@frappe.whitelist()
def get_party_details(party=None, party_type="Customer", ignore_permissions=False):

	if not party:
		return {}

	if not frappe.db.exists(party_type, party):
		frappe.throw(_("{0}: {1} does not exists").format(party_type, party))

	return _get_party_details(party, party_type, ignore_permissions)

def _get_party_details(party=None, party_type="Customer", ignore_permissions=False):

	out = frappe._dict({
		party_type.lower(): party
	})

	if not ignore_permissions and not frappe.has_permission(party_type, "read", party):
		frappe.throw(_("Not permitted for {0}").format(party), frappe.PermissionError)

	set_organisation_details(out, party, party_type)
	
	party = frappe.get_doc(party_type, party)
	
	set_address_details(out, party, party_type)
	set_contact_details(out, party, party_type)
	set_other_values(out, party, party_type)

	return out

def set_organisation_details(out, party, party_type):
	
	organisation = None
	
	if party_type == 'Lead':
		organisation = frappe.db.get_value("Lead", {"name": party}, "company_name")
	elif party_type == 'Customer':
		organisation = frappe.db.get_value("Customer", {"name": party}, "customer_name")
	elif party_type == 'Opportunity':
		organisation = frappe.db.get_value("Opportunity", {"name": party}, "customer_name")
	elif party_type == 'Supplier':
		organisation = frappe.db.get_value("Supplier", {"name": party}, "supplier_name")
	elif party_type == 'Sales Partner':
		organisation = frappe.db.get_value("Sales Partner", {"name": party})
		
	out.update({'organisation': organisation})
	
def set_address_details(out, party, party_type):
	billing_address_field = "customer_address" if party_type == "Lead" \
		else party_type.lower() + "_address"
	out[billing_address_field] = get_default_address(party_type, party.name)
	
	# address display
	out.address_display = get_address_display(out[billing_address_field])

def set_contact_details(out, party, party_type):

	if party_type == "Lead":
		if not party.company_name:
			out.update({
				"contact_person": None,
				"contact_display": party.lead_name,
				"contact_email": party.email_id,
				"contact_mobile": party.mobile_no,
				"contact_phone": party.phone,
			})
			return
	elif party_type == "Opportunity":
		out.update({
				"contact_display": party.party_name,
				"contact_person": party.contact_person,
				"contact_email": party.contact_email,
				"contact_mobile": party.contact_mobile,
		})
			
	out.contact_person = get_default_contact(party_type, party.name)
	
	if out.contact_person:
		out.update(get_contact_details(out.contact_person))

def set_other_values(out, party, party_type):
	# copy
	if party_type=="Customer":
		to_copy = ["customer_name", "customer_group", "territory", "language"]
	else:
		to_copy = ["supplier_name", "supplier_type", "language"]
	for f in to_copy:
		out[f] = party.get(f)