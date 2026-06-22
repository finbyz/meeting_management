import json
import os
import sys
import threading
import time

RESET = "\033[0m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_CYAN = "\033[96m"


def show_loading(message, stop_event):
	dots = ""
	while not stop_event.is_set():
		dots = "." if dots == "..." else dots + "."
		sys.stdout.write(f"\r{BRIGHT_GREEN}{message}{dots:<3}{RESET}")
		sys.stdout.flush()
		time.sleep(0.4)

	sys.stdout.write(f"\r{BRIGHT_GREEN}{message}... Done{RESET}\n")
	sys.stdout.flush()


def run_with_loading(message, func):
	stop_event = threading.Event()
	thread = threading.Thread(target=show_loading, args=(message, stop_event))
	thread.start()

	try:
		return func()
	finally:
		stop_event.set()
		thread.join()


def after_migrate():
	create_custom_fields()
	# create_property_setter()


def create_custom_fields():
	def task():
		CUSTOM_FIELDS = {}

		path = os.path.join(
			os.path.dirname(__file__),
			"meeting_management/custom_fields",
		)

		for file in os.listdir(path):
			with open(os.path.join(path, file)) as f:
				CUSTOM_FIELDS.update(json.load(f))

		from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

		create_custom_fields(CUSTOM_FIELDS)

	run_with_loading("Creating/Updating Custom Fields", task)


def create_property_setter():
	def task():
		from frappe import make_property_setter

		PPS = {}

		path = os.path.join(
			os.path.dirname(__file__),
			"meeting_management/property_setter",
		)

		for file in os.listdir(path):
			with open(os.path.join(path, file)) as f:
				args = json.load(f)
				PPS.update(args)

		for row in PPS:
			for field in PPS[row]:
				if isinstance(field.get("value"), list):
					field["value"] = json.dumps(field["value"])

				if field.get("field_name"):
					field["fieldname"] = field.get("field_name")

				make_property_setter(field, is_system_generated=False)

	run_with_loading("Creating/Updating Property Setter", task)