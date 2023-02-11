
# -*- coding: utf-8 -*-
# Copyright (c) 2017, FinByz Tech Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, db, _
import json
from frappe.utils import cint, getdate, get_fullname, get_url_to_form,now_datetime
# from erpnext.accounts.party import get_party_details
from meeting_management.meeting_management.doctype.meeting_schedule.meeting_schedule import get_party_details
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from frappe.email.smtp import SMTPServer
import smtplib
from frappe.utils.user import get_user_fullname
import re
from email.mime.multipart import MIMEMultipart
from email import encoders
from frappe.email.smtp import SMTPServer
import smtplib
from datetime import datetime
import datetime
from frappe.utils import get_datetime

class Meeting(Document):
	
	def validate(self):
		if self.party_type and self.party:
			data = get_party_details(party_type=self.party_type,party=self.party)
			if data:
				self.contact_person = data.contact_person
				self.email_id = data.contact_email
				self.mobile_no = data.contact_mobile
				self.contact = data.contact_dispaly
				self.address = data.customer_address
				self.address_display = data.address_display
				self.organization = data.organisation

	def on_submit(self):
		user_name = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"employee_name")
		url = get_url_to_form("Meeting", self.name)
		if user_name:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ user_name + " Met "+ str(self.contact_person) + " On "+ self.meeting_from +"<br>" + self.discussion.replace('\n', "<br>")
		else:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ frappe.session.user + " Met "+ str(self.contact_person)+ " On "+ self.meeting_from +"<br>" + self.discussion.replace('\n', "<br>")

		cm = frappe.new_doc("Comment")
		cm.subject = self.name
		cm.comment_type = "Comment"
		cm.content = discussed
		cm.reference_doctype = self.party_type
		cm.reference_name = self.party
		cm.comment_email = frappe.session.user
		cm.comment_by = user_name
		cm.save(ignore_permissions=True)
		if self.party_type == "Lead":
			target_lead = frappe.get_doc("Lead", self.party)
			target_lead.turnover = self.turnover
			target_lead.industry = self.industry
			target_lead.business_specifics = self.business_specifics
			target_lead.contact_by = self.contact_by
			target_lead.contact_date = self.contact_date
			if not target_lead.email_id:
				target_lead.email_id = self.email_id
			if not target_lead.lead_name:
				target_lead.lead_name = self.contact_person
			if not target_lead.mobile_no:
				target_lead.mobile_no = self.mobile_no
			target_lead.save(ignore_permissions=True)

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	#filters = json.loads(filters)
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Meeting", filters)

	data = frappe.db.sql("""
			select 
				name, meeting_from, meeting_to, organization, party
			from 
				`tabMeeting`
			where
				(meeting_from <= %(end)s and meeting_to >= %(start)s) {conditions}
			""".format(conditions=conditions),
				{
					"start": start,
					"end": end
				}, as_dict=True, update={"allDay": 0})

	if not data:
		return []
		
	data = [x.name for x in data]

	return frappe.db.get_list("Meeting",
		{ "name": ("in", data), "docstatus":1 },
		["name", "meeting_from", "meeting_to", "organization", "party"]
	)

@frappe.whitelist()
def send_mail(self):
	res = json.loads(self)
	if not res.get('meeting_party_representative'):
		msgprint(_("Please enter Contact in Meeting Party Representative"))
		return

	CRLF = "\r\n"
	default_sender_name, default_sender =frappe.db.get_value('Email Account',{'default_outgoing':1},['name','email_id'])
	if not default_sender:
		frappe.throw("Please Setup Default Outgoing Email Account.")
	organizer = "ORGANIZER;CN=" +default_sender+":mailto:"+default_sender
	dtstamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	dtstart = get_datetime(res.get('meeting_from')).strftime("%Y%m%dT%H%M%S")
	dtend = get_datetime(res.get('meeting_to')).strftime("%Y%m%dT%H%M%S")
	attendees=[]
	if res.get('cc_to'):
		cc = res.get('cc_to').replace(' ','')
		attendees = cc.split(',')
	for row in res.get('meeting_party_representative'):
		attendees.append(row.get('email_id'))
		
	subject = "Completed Meeting on %s " % get_datetime(res.get('meeting_from')).strftime("%A %d-%b-%Y")
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
	msg['Reply-To']=res.get('email_id')
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject
	msg['From'] = res.get('email_id')
	msg['To'] = ",".join(attendees)
	msg.add_header('Content-class', 'urn:content-classes:calendarmessage')

	email_body = ""
	# part_email = MIMEText(ical,'calendar;method=REQUEST')
	if res.get('discussion'):
		body = ""
		main_body = '{}'.format(res.get('discussion'))
		for idx ,row in enumerate(res.get('actionables')):
			Date = frappe.format(res.get('actionables')[idx].get('expected_completion_date') , {'fieldtype': 'Date'})
			body += '<br><br><strong>Actionable:</strong> {}<br> <strong>Responsible:</strong> {}<br><strong>Expected Completion Date:</strong>{}'.format( res.get('actionables')[idx].get('actionable') ,res.get('actionables')[idx].get('responsible'),Date)
		main_body = main_body + body
		email_body = MIMEText(main_body, 'html')

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
	frappe.msgprint(_("Mail sent successfully"))

	doc = frappe.new_doc("Communication")
	doc.subject = subject
	doc.communication_medium = "Email"
	doc.sender = default_sender
	doc.recipients = res.get('email_id')
	doc.cc = res.get('cc_to')
	doc.content = res.get('discussion')
	doc.communication_type = "Communication"
	doc.status="Linked"
	doc.sent_or_received = "Sent"
	doc.sender_full_name = get_user_fullname(frappe.session.user)
	doc.reference_doctype = res.get('doctype')
	doc.reference_name = res.get('name')
	doc.reference_owner = frappe.session.user
	doc.user = frappe.session.user
	doc.email_account = default_sender_name
	doc.save(ignore_permissions=True)