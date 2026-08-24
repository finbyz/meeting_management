# Copyright (c) 2023, Finbyz Tech PVT LTD and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.query_builder import DocType
from frappe.model.mapper import get_mapped_doc
from typing import Any, Dict, Union

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
from datetime import timedelta
class Meeting(Document):
	
	def get_recurrence_rrule(self):
		checked_rows = [row for row in self.recurring_meeting if row.check]
		if not checked_rows:
			return None

		day_map = {
			"Monday": "MO",
			"Tuesday": "TU",
			"Wednesday": "WE",
			"Thursday": "TH",
			"Friday": "FR",
			"Saturday": "SA",
			"Sunday": "SU",
		}

		byday = [day_map[row.day] for row in checked_rows if row.day in day_map]
		# Ensure sorted/consistent order to prevent duplicate/inconsistent RRULES
		byday = sorted(list(set(byday)), key=lambda d: ["SU", "MO", "TU", "WE", "TH", "FR", "SA"].index(d))

		end_dates = [getdate(row.end_date) for row in checked_rows if row.end_date]
		if not end_dates:
			return None
		latest_end_date = max(end_dates)

		# Format UNTIL in UTC format: YYYYMMDDTHHMMSSZ
		until_str = latest_end_date.strftime("%Y%m%d") + "T235959Z"

		return f"RRULE:FREQ=WEEKLY;BYDAY={','.join(byday)};UNTIL={until_str}"

	def before_update_after_submit(self):
		self.create_agenda()
		self.create_task()
	def validate(self):
		# self.update_description()
		if self.meeting_to and self.meeting_to<self.meeting_from:
			frappe.throw(_("Meeting To cannot be less than Meeting From"))
		if self.party_type and self.party:
			data = get_party_details(party_type=self.party_type,party=self.party)
			if data:
				self.contact_p = data.contact_person
				self.email_id = data.contact_email
				self.mobile_no = data.contact_mobile
				self.contact = data.contact_dispaly
				self.address = data.customer_address
				self.address_display = data.address_display
				self.organization = data.organisation
		
		if self.meeting_from and self.meeting_to:
			if self.meeting_from > self.meeting_to:
				frappe.throw(_("Meeting To Date must be after Meeting From Date"))

	def on_submit(self):	
		self.create_event()
		self.create_agenda()
		self.create_task()
		user_name = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"employee_name")
		url = get_url_to_form("Meeting", self.name)
		if user_name:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ user_name + " Met "+ str(self.contact_p) + " On "+ self.meeting_from +"<br>"
		else:
			discussed = "<strong><a href="+url+">"+self.name+"</a>: </strong>"+ frappe.session.user + " Met "+ str(self.contact_p)+ " On "+ self.meeting_from +"<br>"

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
				target_lead.lead_name = self.contact_p
			if not target_lead.mobile_no:
				target_lead.mobile_no = self.mobile_no
			target_lead.save(ignore_permissions=True)
	# def create_agenda(self):
	# 	for row in self.agenda_details:
	# 		if row.write_agenda and row.has_task:
	# 			self.append("tasks", {
	# 				"subject": row.write_agenda,
	# 				"user_id":frappe.session.user,
	# 				"start_date":self.meeting_from,
	# 				"due_date":self.meeting_to,
					# "is_meetin_task":1
	# 			})
	# 	self.save(ignore_permissions=True)
	def create_agenda(self):
		if not self.agenda_details:
			return

		parent_task = None

		for row in self.agenda_details:
			subject = (row.write_agenda or "").strip()
			if not row.has_task or not subject:
				continue

			task_row = self.get_existing_agenda_task_row(subject)
			if task_row and task_row.task and frappe.db.exists("SNM Task", task_row.task):
				self.sync_agenda_task_parent(task_row)
				continue

			existing_task = self.get_existing_agenda_task(subject)
			if existing_task:
				existing_parent_task = frappe.db.get_value("SNM Task", existing_task, "parent_task")
				if existing_parent_task:
					self.ensure_agenda_parent_task_row(existing_parent_task)
				if not task_row:
					self.append_agenda_task_row(subject, task=existing_task, parent_task=existing_parent_task)
				else:
					task_row.task = existing_task
					task_row.parent_task = existing_parent_task
					task_row.is_meeting_task = 1
				continue

			if not parent_task:
				parent_task = self.get_or_create_agenda_parent_task()
				self.ensure_agenda_parent_task_row(parent_task)

			if task_row:
				task_row.parent_task = parent_task
				task_row.is_meeting_task = 1
				continue

			self.append_agenda_task_row(subject, parent_task=parent_task)

	def ensure_agenda_parent_task_row(self, parent_task):
		if not parent_task:
			return

		parent_row = self.get_existing_task_row_by_task(parent_task)
		if parent_row:
			parent_row.has_sub_task = 1
			parent_row.is_meeting_task = 1
			parent_row.meeting = self.name
			return

		parent = frappe.get_doc("SNM Task", parent_task)
		self.append("tasks", {
			"task": parent.name,
			"task_no": parent.task_no,
			"subject": parent.subject,
			"user": parent.allocated_by,
			"status": parent.status,
			"priority": parent.priority,
			"start_date": parent.start_date,
			"due_date": parent.due_date,
			"has_sub_task": 1,
			"meeting": self.name,
			"description": parent.description,
			"is_meeting_task": 1
		})

	def sync_agenda_task_parent(self, task_row):
		parent_task = frappe.db.get_value("SNM Task", task_row.task, "parent_task")
		if parent_task:
			task_row.parent_task = parent_task
			self.ensure_agenda_parent_task_row(parent_task)
		task_row.is_meeting_task = 1
		task_row.meeting = self.name

	def append_agenda_task_row(self, subject, task=None, parent_task=None):
		self.append("tasks", {
			"task": task,
			"subject": subject,
			"user": frappe.session.user,
			"start_date": self.meeting_from,
			"due_date": self.meeting_to,
			"parent_task": parent_task,
			"meeting": self.name,
			"is_meeting_task": 1
		})

	def get_existing_agenda_task_row(self, subject):
		for row in self.tasks:
			if row.has_sub_task and row.task and not row.parent_task:
				continue
			if self.normalize_task_subject(row.subject) == subject:
				if row.task and not frappe.db.exists("SNM Task", row.task):
					row.task = None
				return row

	def get_existing_task_row_by_task(self, task):
		for row in self.tasks:
			if row.task == task:
				return row

	def get_existing_agenda_task(self, subject):
		tasks = frappe.get_all(
			"SNM Task",
			filters={
				"meeting": self.name,
				"is_meeting_task": 1,
				"parent_task": ["is", "set"],
			},
			fields=["name", "subject"],
		)

		for task in tasks:
			if self.normalize_task_subject(task.subject) == subject:
				return task.name

	def get_or_create_agenda_parent_task(self):
		parent_task = frappe.db.get_value(
			"SNM Task",
			{
				"meeting": self.name,
				"parent_task": ["is", "not set"]
			},
			"name"
		)

		if parent_task:
			return parent_task

		parent_task = frappe.get_doc({
			"doctype": "SNM Task",
			"subject": self.meeting_title or self.name,
			"meeting": self.name,
			"is_meeting_task": 1,
			"is_group": 1,
			"allocated_by": frappe.session.user,
			"start_date": self.meeting_from,
			"due_date": self.meeting_to,
		}).insert(ignore_permissions=True)

		return parent_task.name

	def normalize_task_subject(self, subject):
		subject = (subject or "").strip()
		parts = subject.split(" - ", 1)
		if parts[0].replace(".", "").isdigit():
			return parts[1].strip() if len(parts) > 1 else ""
		return subject
	@frappe.whitelist()
	def get_user(self):
		if self.user_type:
			users = frappe.get_list("User", filters={"custom_user_type": self.user_type,"enabled":1}, pluck="name")
			if not users: return frappe.throw(_("No users found with user type {0}").format(self.user_type))

			for row in users:
				self.append("meeting_party_representative",{
					"user": row
				})
	
	@frappe.whitelist()
	def create_task(self):
		if not self.tasks:
			return
		for row in self.tasks:
			if not row.task:
				task = frappe.new_doc("SNM Task")
				task.subject = row.subject
				task.allocated_by = row.user if row.user else frappe.session.user
				task.priority = row.priority
				task.status = row.status
				task.start_date = row.start_date
				task.due_date = row.due_date
				task.meeting = self.name
				task.description = row.description
				task.is_meeting_task = row.is_meeting_task
				if row.has_sub_task:
					task.is_group = 1
				if row.parent_task:
					task.parent_task = row.parent_task
				task.department = frappe.db.get_value("Employee",{"user_id":row.user},"department")
				task.save(ignore_permissions=True)
				row.task = task.name
				row.task_no = task.task_no
	
	# def update_description(self):
	# 	frappe.throw(":::::::::")
	# 	if not self.tasks:
	# 		return
	# 	for row in self.tasks:
	# 		if not row.task:
	# 			return
	# 		if row.has_value_changed("desctiption"):
	# 			frappe.db.set_value("SNM Task", row.task, "description", self.description)
	def create_event(self):

		# Create Main Event
		main_event = frappe.new_doc("Event")
		main_event.subject = self.meeting_title
		main_event.event_type = "Private"
		main_event.starts_on = self.meeting_from
		main_event.ends_on = self.meeting_to
		# main_event.description = self.discussion
		main_event.save(ignore_permissions=True)

		# -----------------------------
		# Recurring Events
		# -----------------------------

		weekdays = {
			"Monday": 0,
			"Tuesday": 1,
			"Wednesday": 2,
			"Thursday": 3,
			"Friday": 4,
			"Saturday": 5,
			"Sunday": 6,
		}

		start_datetime = get_datetime(self.meeting_from)
		end_datetime = get_datetime(self.meeting_to)

		start_date = start_datetime.date()

		for row in self.recurring_meeting:

			# Skip unchecked rows
			if not row.check:
				continue

			if not row.day or not row.end_date:
				continue

			target_weekday = weekdays.get(row.day)

			current_date = start_date
			end_date = getdate(row.end_date)

			while current_date <= end_date:

				# Match weekday
				if current_date.weekday() == target_weekday:

					# Skip main meeting date
					if current_date != start_date:

						recurring_event = frappe.new_doc("Event")

						recurring_event.subject = f"{self.meeting_title}"
						recurring_event.event_type = "Private"

						# Keep same time
						recurring_event.starts_on = start_datetime.replace(
							year=current_date.year,
							month=current_date.month,
							day=current_date.day
						)

						recurring_event.ends_on = end_datetime.replace(
							year=current_date.year,
							month=current_date.month,
							day=current_date.day
						)

						# recurring_event.description = self.discussion

						recurring_event.save(ignore_permissions=True)

				current_date += timedelta(days=1)

		return main_event.name
	# def create_event(self):
	# 	event = frappe.new_doc("Event")
	# 	event.subject = self.name
	# 	event.event_type = "Private"
	# 	event.starts_on = self.meeting_from
	# 	event.ends_on = self.meeting_to
	# 	event.save(ignore_permissions=True)
	# 	# event.custom_contact_person=self.contact_p
	# 	event.description=self.discussion
	# 	return event.name
	
	

from typing import Any

@frappe.whitelist()
def get_events(
	start: str,
	end: str,
	filters: dict[str, Any] | None = None
) -> list:
	"""Returns events for Gantt / Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	#filters = json.loads(filters)
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Meeting", filters)
	Meeting = DocType("Meeting")

	# data = frappe.db.sql("""
	# 		select 
	# 			name, meeting_from, meeting_to, organization, party
	# 		from 
	# 			`tabMeeting`
	# 		where
	# 			(meeting_from <= %(end)s and meeting_to >= %(start)s) {conditions}
	# 		""".format(conditions=conditions),
	# 			{
	# 				"start": start,
	# 				"end": end
	# 			}, as_dict=True, update={"allDay": 0})
	data = (
		frappe.qb.from_(Meeting)
		.select(
			Meeting.name,
			Meeting.meeting_from,
			Meeting.meeting_to,
			Meeting.organization,
			Meeting.party,
		)
		.where(Meeting.meeting_from <= end)
		.where(Meeting.meeting_to >= start)
	).run(as_dict=True)
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
		frappe.throw(_("Please Setup Default Outgoing Email Account."))
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
		if res.get('actionables'):
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


import frappe
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# @frappe.whitelist()
# def create_google_meet(event_name):

#     # ERPNext Event
#     event = frappe.get_doc("Meeting", event_name)

#     # Google Settings
#     google_settings = frappe.get_single("Google Settings")

#     client_id = google_settings.client_id
#     client_secret = google_settings.get_password("client_secret")

#     # Fetch Authorized Google Calendar
#     google_calendar = frappe.get_last_doc(
#         "Google Calendar")

#     if not google_calendar.refresh_token:
#         frappe.throw("Google Calendar is not authorized.")

#     # Create Credentials
#     creds = Credentials(
#         token=None,
#         refresh_token=google_calendar.refresh_token,
#         token_uri="https://oauth2.googleapis.com/token",
#         client_id=client_id,
#         client_secret=client_secret
#     )

#     # Refresh Access Token
#     # creds.refresh(Request())

#     # Google Calendar Service
#     service = build(
#         "calendar",
#         "v3",
#         credentials=creds
#     )

#     # Event Payload
#     body = {
#         "summary": event.meeting_title,
#         "description": event.discussion or "",
#         "start": {
#             "dateTime": event.meeting_from.isoformat(),
#             "timeZone": "Asia/Kolkata"
#         },
#         "end": {
#             "dateTime": event.meeting_to.isoformat(),
#             "timeZone": "Asia/Kolkata"
#         },
#         "conferenceData": {
#             "createRequest": {
#                 "requestId": frappe.generate_hash(length=10)
#             }
#         },
#         "attendees": []
#     }

#     # Add Participants
#     for participant in event.meeting_party_representative:

#         if participant.user:
#             body["attendees"].append({
#                 "email": participant.user
#             })

#     created_event = service.events().insert(
#         calendarId="primary",
#         body=body,
#         conferenceDataVersion=1,
#         sendUpdates="all"
#     ).execute()

#     meet_link = created_event.get("hangoutLink")

#     event.db_set(
#         "meet_link",
#         meet_link
#     )

#     return {
#         "meet_link": meet_link,
#         "google_event_id": created_event.get("id")
#     }

@frappe.whitelist()
def create_google_meet(event_name:str):

	# ERPNext Event
	event = frappe.get_doc("Meeting", event_name)

	# Fetch Authorized Google Calendar
	google_calendar = frappe.get_last_doc("Google Calendar")

	if not google_calendar or not google_calendar.name:
		frappe.throw(_("Google Calendar is not authorized."))

	from frappe.integrations.doctype.google_calendar.google_calendar import get_google_calendar_object
	service, google_calendar_doc = get_google_calendar_object(google_calendar.name)

	# Add Participants
	attendees = []
	for participant in event.meeting_party_representative:
		email = participant.email_id or participant.user
		if email:
			attendees.append({
				"email": email
			})

	# Fetch all Frappe Event records linked to this meeting (both main and recurring)
	frappe_events = frappe.get_all(
		"Event",
		filters={"subject": event_name},
		fields=["name", "starts_on", "ends_on", "google_calendar_event_id"],
		order_by="starts_on asc"
	)

	calendar_id = google_calendar_doc.google_calendar_id or "primary"
	rrule = event.get_recurrence_rrule()

	import pytz
	from frappe.utils.data import get_system_timezone

	def get_utc_start_time_str(local_dt):
		system_tz = pytz.timezone(get_system_timezone() or "UTC")
		if local_dt.tzinfo is None:
			local_dt = system_tz.localize(local_dt)
		utc_dt = local_dt.astimezone(pytz.utc)
		return utc_dt.strftime("%Y%m%dT%H%M%SZ")

	if rrule:
		# -----------------------------
		# Recurring Event flow
		# -----------------------------
		# In Google Calendar, we create/update a single parent event with the RRULE recurrence rule.
		# Google Calendar automatically handles all instance generation.
		
		parent_fe = frappe_events[0] if frappe_events else None
		
		starts_on = parent_fe.starts_on if parent_fe else event.meeting_from
		ends_on = parent_fe.ends_on if parent_fe else event.meeting_to
		parent_g_id = parent_fe.google_calendar_event_id if parent_fe else None

		body = {
			"summary": event.meeting_title,
			"description": event.discussion or "",
			"start": {
				"dateTime": get_datetime(starts_on).isoformat(),
				"timeZone": "Asia/Kolkata"
			},
			"end": {
				"dateTime": get_datetime(ends_on).isoformat(),
				"timeZone": "Asia/Kolkata"
			},
			"recurrence": [rrule],
			"attendees": attendees
		}

		conference_data = None
		meet_link = None
		
		if parent_g_id:
			try:
				g_event = service.events().get(calendarId=calendar_id, eventId=parent_g_id).execute()
				conference_data = g_event.get("conferenceData")
				meet_link = g_event.get("hangoutLink")
			except Exception:
				parent_g_id = None

		if not conference_data:
			body["conferenceData"] = {
				"createRequest": {
					"requestId": frappe.generate_hash(length=10),
					"conferenceSolutionKey": {"type": "hangoutsMeet"}
				}
			}

		if parent_g_id:
			g_event = service.events().update(
				calendarId=calendar_id,
				eventId=parent_g_id,
				body=body,
				conferenceDataVersion=1,
				sendUpdates="all"
			).execute()
		else:
			g_event = service.events().insert(
				calendarId=calendar_id,
				body=body,
				conferenceDataVersion=1,
				sendUpdates="all"
			).execute()

		parent_g_id = g_event.get("id")
		meet_link = g_event.get("hangoutLink")

		# Update all corresponding Frappe Event documents with calculated instance IDs
		if frappe_events:
			for idx, fe in enumerate(frappe_events):
				if idx == 0:
					fe_g_id = parent_g_id
				else:
					utc_str = get_utc_start_time_str(get_datetime(fe.starts_on))
					fe_g_id = f"{parent_g_id}_{utc_str}"

				update_dict = {
					"google_calendar": google_calendar.name,
					"google_calendar_id": calendar_id,
					"google_calendar_event_id": fe_g_id,
					"google_meet_link": meet_link
				}
				if frappe.get_meta("Event").has_field("custom_meet_link"):
					update_dict["custom_meet_link"] = meet_link

				frappe.db.set_value("Event", fe.name, update_dict, update_modified=False)

			# frappe.db.commit()

	else:
		# -----------------------------
		# Non-recurring Event flow (single event)
		# -----------------------------
		fe = frappe_events[0] if frappe_events else None
		
		starts_on = fe.starts_on if fe else event.meeting_from
		ends_on = fe.ends_on if fe else event.meeting_to
		g_id = fe.google_calendar_event_id if fe else None

		body = {
			"summary": event.meeting_title,
			"description": event.discussion or "",
			"start": {
				"dateTime": get_datetime(starts_on).isoformat(),
				"timeZone": "Asia/Kolkata"
			},
			"end": {
				"dateTime": get_datetime(ends_on).isoformat(),
				"timeZone": "Asia/Kolkata"
			},
			"attendees": attendees
		}

		conference_data = None
		meet_link = None
		
		if g_id:
			try:
				g_event = service.events().get(calendarId=calendar_id, eventId=g_id).execute()
				conference_data = g_event.get("conferenceData")
				meet_link = g_event.get("hangoutLink")
			except Exception:
				g_id = None

		if not conference_data:
			body["conferenceData"] = {
				"createRequest": {
					"requestId": frappe.generate_hash(length=10),
					"conferenceSolutionKey": {"type": "hangoutsMeet"}
				}
			}

		if g_id:
			g_event = service.events().update(
				calendarId=calendar_id,
				eventId=g_id,
				body=body,
				conferenceDataVersion=1,
				sendUpdates="all"
			).execute()
		else:
			g_event = service.events().insert(
				calendarId=calendar_id,
				body=body,
				conferenceDataVersion=1,
				sendUpdates="all"
			).execute()

		parent_g_id = g_event.get("id")
		meet_link = g_event.get("hangoutLink")

		if fe:
			update_dict = {
				"google_calendar": google_calendar.name,
				"google_calendar_id": calendar_id,
				"google_calendar_event_id": parent_g_id,
				"google_meet_link": meet_link
			}
			if frappe.get_meta("Event").has_field("custom_meet_link"):
				update_dict["custom_meet_link"] = meet_link

			frappe.db.set_value("Event", fe.name, update_dict, update_modified=False)
			# frappe.db.commit()

	if meet_link:
		event.db_set("meet_link", meet_link)

	return {
		"meet_link": meet_link,
		"google_event_id": parent_g_id
	}

@frappe.whitelist()
def create_follow_up_meeting(
	parent_meeting: str,
	subject: str,
	description: str | None = None,
	follow_up_date: str | None = None,
	contact_person: str | None = None,
	follow_end_date: str | None = None,
) -> str:

	# Fetch Parent Meeting
	parent_doc = frappe.get_doc("Meeting", parent_meeting)

	# Create New Follow Up Meeting
	m = frappe.new_doc("Meeting")

	m.meeting_title = subject
	m.discussion = description
	m.meeting_from = follow_up_date
	m.meeting_to = follow_end_date
	m.parent_meeting = parent_meeting
	m.contact_person = contact_person

	# Copy values from parent meeting
	m.meeting_arranged_by = parent_doc.meeting_arranged_by
	m.contact_p = parent_doc.contact_p
	m.meeting_type = parent_doc.meeting_type
	m.user_type = parent_doc.user_type
	m.meeting_party_representative = parent_doc.meeting_party_representative
	
	m.insert(ignore_permissions=True ,ignore_mandatory=True)
	return m.name

@frappe.whitelist()
def create_task_from_dialog(meeting: str, data: Union[str, Dict[str, Any]]):
	if isinstance(data, str):
		data = json.loads(data)
	assigned_users = data.get("assigned_users") or []
	if isinstance(assigned_users, str):
		try:
			assigned_users = json.loads(assigned_users)
		except ValueError:
			assigned_users = [assigned_users]

	# -----------------------------------
	# FIND PARENT TASK
	# -----------------------------------
	parent_task = frappe.db.get_value(
		"SNM Task",
		{
			"meeting": meeting,
			"parent_task": ["is", "not set"]
		},
		"name"
	)

	# -----------------------------------
	# CREATE PARENT IF NOT EXISTS
	# -----------------------------------
	if not parent_task:

		parent = frappe.new_doc("SNM Task")
		parent.subject = frappe.db.get_value("Meeting", meeting, "meeting_title") or meeting
		parent.meeting = meeting
		parent.allocated_by=frappe.session.user
		parent.is_group = 1

		parent.insert()

		parent_task = parent.name

	# -----------------------------------
	# CREATE CHILD TASK
	# -----------------------------------
	child = frappe.new_doc("SNM Task")
	child.subject = data.get("subject")
	child.description = data.get("description")
	child.due_date = data.get("due_date")
	child.start_date=data.get("start_date")
	child.allocated_by = data.get("assigned_to")

	child.meeting = meeting
	child.parent_task = parent_task
	for row in assigned_users:
		user = row.get("user") if isinstance(row, dict) else row
		if user:
			child.append("assigned_users", {"user": user})

	child.insert()

	return child.name
def get_permission_query_conditions(user=None, doctype=None):
	user = user or frappe.session.user

	if user == "Administrator":
		return ""

	user = frappe.db.escape(user)

	return f"""
		(
			`tabMeeting`.`email_id` = {user}
			OR `tabMeeting`.`meeting_arranged_by` = {user}
			OR EXISTS (
				SELECT 1
				FROM `tabMeeting Party Representative`
				WHERE `tabMeeting Party Representative`.`parent` = `tabMeeting`.`name`
				AND `tabMeeting Party Representative`.`parenttype` = 'Meeting'
				AND `tabMeeting Party Representative`.`parentfield` = 'meeting_party_representative'
				AND `tabMeeting Party Representative`.`user` = {user}
			)
		)
	"""


def has_permission(doc, user=None, permission_type=None):
	user = user or frappe.session.user

	if user == "Administrator":
		return True

	if doc.email_id == user or doc.meeting_arranged_by == user:
		return True

	for row in doc.get("meeting_party_representative") or []:
		if row.user == user:
			return True

	return False
