# # Copyright (c) 2026, Shivangi and contributors
# # For license information, please see license.txt

# import frappe
# import json
# from frappe.model.document import Document
# from frappe import _, throw
# from frappe.desk.form.assign_to import clear, close_all_assignments
# from frappe.utils import get_link_to_form, get_url_to_form
# from frappe.desk.form.assign_to import add as add_assignment

# class ParentIsGroupError(frappe.ValidationError):
# 	pass


# class SNMTask(Document):

# 	def validate(self):
# 		self.assign_user()
# 		self.set_group_task()
# 		self.update_depends_on()
# 		self.validate_parent_is_group()
# 		self.validate_due_date()
# 		self.get_dept()
# 		self.update_description()
# 		self.update_snm_description()
# 		# self.update_child_description()
# 		self.update_subject()
# 	def on_update(self):
# 		self.update_child_description()
# 	def before_insert(self):
# 		self.get_task_no()

# 	def after_insert(self):
# 		self.create_child_tasks()
# 		self.update_meet()
# 	def on_update(self):
# 		self.create_child_tasks()
# 		self.populate_depends_on()
# 		self.unassign_todo()
# 		# self.update_subject()
# 	# def assign_user(self):
# 	# 	for row in self.assigned_users:
# 	# 		if not row.user:
# 	# 			continue

# 	# 		exists = frappe.db.exists(
# 	# 			"ToDo",
# 	# 			{
# 	# 				"reference_type": self.doctype,
# 	# 				"reference_name": self.name,
# 	# 				"allocated_to": row.user,
# 	# 				"status": "Open",
# 	# 			},
# 	# 		)

# 	# 		if exists:
# 	# 			continue

# 	# 		todo = frappe.get_doc(
# 	# 			{
# 	# 				"doctype": "ToDo",
# 	# 				"allocated_to": row.user,
# 	# 				"reference_type": self.doctype,
# 	# 				"reference_name": self.name,
# 	# 				"description": self.subject or self.name,
# 	# 				"status": "Open",
# 	# 			}
# 	# 		)
# 	# 		todo.insert(ignore_permissions=True)
# 	def assign_user(self):
# 		current_users = [row.user for row in self.assigned_users if row.user]

# 		# Create ToDo for selected users
# 		for user in current_users:
# 			exists = frappe.db.exists(
# 				"ToDo",
# 				{
# 					"reference_type": self.doctype,
# 					"reference_name": self.name,
# 					"allocated_to": user,
# 					"status": "Open",
# 				},
# 			)

# 			if exists:
# 				continue

# 			frappe.get_doc(
# 				{
# 					"doctype": "ToDo",
# 					"allocated_to": user,
# 					"reference_type": self.doctype,
# 					"reference_name": self.name,
# 					"description": self.subject or self.name,
# 					"status": "Open",
# 				}
# 			).insert(ignore_permissions=True)

# 		# Remove ToDo if user removed from assigned_users
# 		existing_todos = frappe.get_all(
# 			"ToDo",
# 			filters={
# 				"reference_type": self.doctype,
# 				"reference_name": self.name,
# 				"status": "Open",
# 			},
# 			fields=["name", "allocated_to"],
# 		)

# 		for todo in existing_todos:
# 			if todo.allocated_to not in current_users:
# 				frappe.delete_doc("ToDo", todo.name, ignore_permissions=True)
# 	def validate_due_date(self):
# 		if not self.due_date:
# 			return
# 		if not self.depends_on:
# 			return
		
# 		for row in self.depends_on:
# 			if row.due_date and self.due_date < row.due_date:
# 				throw(_("Due Date of Task cannot be before Due Date of dependent Task {0}").format(
# 					get_link_to_form("SNM Task", row.task)
# 				))	

# 	def set_group_task(self):

# 		# Auto enable group if child rows exist
# 		if self.depends_on and not self.is_group:
# 			self.is_group = 1

# 	def validate_parent_is_group(self):

# 		if self.parent_task:

# 			if not frappe.db.get_value(
# 				"SNM Task",
# 				self.parent_task,
# 				"is_group"
# 			):

# 				frappe.throw(
# 					_("Parent Task {0} must be a Group Task").format(
# 						get_link_to_form("SNM Task", self.parent_task)
# 					),
# 					ParentIsGroupError,
# 				)

# 	def populate_depends_on(self):
# 		if self.parent_task and not self.created_from_parent:

# 			parent = frappe.get_doc("SNM Task", self.parent_task)
# 			existing_tasks = [row.task for row in parent.depends_on]

# 			if self.name not in existing_tasks:

# 				parent.append(
# 					"depends_on",
# 					{
# 						"doctype": "Task Depends On",
# 						"task": self.name,
# 						"subject": self.subject,
# 						"description": self.description,
# 						"priority": self.priority,
# 						"status":self.status,
# 						"parent_task": self.parent_task,
# 					}
# 				)

# 				parent.flags.ignore_child_creation = True

# 				parent.save(ignore_permissions=True)
			
# 	def unassign_todo(self):

# 		if self.status == "Completed":
# 			close_all_assignments(self.doctype, self.name)

# 		if self.status == "Cancelled":
# 			clear(self.doctype, self.name)

# 	def update_depends_on(self):

# 		depends_on_tasks = ""

# 		for d in self.depends_on:
# 			if not d.parent_task:
# 				d.parent_task = self.name

# 			if d.task and d.task not in depends_on_tasks:
# 				depends_on_tasks += d.task + ","

# 		self.depends_on_tasks = depends_on_tasks

# 	def create_child_tasks(self):

# 		# Prevent recursive save loop
# 		if self.flags.ignore_child_creation:
# 			return

# 		if not self.depends_on:
# 			return


# 		for row in self.depends_on:

# 			# Skip if already linked
# 			if row.task:
# 				continue

# 			child_task = frappe.get_doc({
# 				"doctype": "SNM Task",
# 				"subject": row.subject,
# 				"parent_task": self.name,
# 				"allocated_by": frappe.session.user,
# 				"status": row.status,
# 				"priority": row.priority,
# 				"created_from_parent": 1,
# 				"start_date": row.start_date,
# 				"due_date": row.due_date,
# 				"description": row.description,
# 				"created_by":row.user_id
# 			})

# 			child_task.flags.ignore_child_creation = True

# 			child_task.insert(ignore_permissions=True)

# 			# Update only current row
# 			row.db_set("task", child_task.name)
# 			if row.user:
# 				todo = frappe.new_doc("ToDo")
# 				todo.assigned_by = frappe.session.user
# 				todo.reference_type = "SNM Task"
# 				todo.reference_name = child_task.name
# 				todo.priority = child_task.priority
# 				todo.description = child_task.subject
# 				todo.date = child_task.due_date
# 				todo.allocated_to = row.user
# 				todo.status = "Open"
# 				todo.insert(ignore_permissions=True)
# 	def update_description(self):
# 		if not self.meeting:
# 			return
# 		if not self.has_value_changed("description"):
# 			return
# 		row = frappe.db.get_value("Child Tasks",{"parent":self.meeting,"task":self.name},"name")
# 		frappe.db.set_value("Child Tasks",row,"description",self.description)

# 	def update_snm_description(self):
# 		if not self.parent_task:
# 			return
# 		if not self.has_value_changed("description"):
# 			return
# 		row = frappe.db.get_value("Child Tasks",{"parent":self.parent_task,"task":self.name},"name")
# 		frappe.db.set_value("Child Tasks",row,"description",self.description)

# 	def update_child_description(self):
# 		if not self.depends_on:
# 			return
# 		for row in self.depends_on:
# 			if not row.task:
# 				return
# 			if row.has_value_changed("description"):
# 				frappe.db.set_value("Task Depends On",{"name":row.name},"description",self.description)

# 	def on_trash(self):

# 		if check_if_child_exists(self.name):

# 			throw(
# 				_("Child Task exists for this Task. You can not delete this Task.")
# 			)
# 	def update_meet(self):
# 		if not self.meeting:
# 			return

# 		meet = frappe.get_doc("Meeting", self.meeting)

# 		if any(row.task == self.name for row in meet.tasks):
# 			return

# 		meet.append("tasks", {
# 			"task": self.name,
# 			"subject": self.subject,
# 			"user": self.allocated_by,
# 			"status": self.status,
# 			"priority": self.priority,
# 			"start_date": self.start_date,
# 			"due_date": self.due_date,
# 			"parent_task": self.parent_task,
# 			"description": self.description
# 		})

# 		meet.save(ignore_permissions=True)
		
# 	@frappe.whitelist()
# 	def get_task_no(self):

# 		if not self.parent_task:

# 			max_task = frappe.db.sql("""
# 				SELECT MAX(CAST(task_no AS UNSIGNED))
# 				FROM `tabSNM Task`
# 				WHERE parent_task IS NULL OR parent_task = ''
# 			""", as_list=True)[0][0]

# 			if max_task:
# 				self.task_no = str(max_task + 1)
# 			else:
# 				self.task_no = "1"

# 		else:

# 			parent_task_no = frappe.db.get_value(
# 				"SNM Task",
# 				self.parent_task,
# 				"task_no"
# 			)

# 			last_child = frappe.db.get_value(
# 				"SNM Task",
# 				{
# 					"parent_task": self.parent_task,
# 					"task_no": ["is", "set"]
# 				},
# 				"task_no",
# 				order_by="creation desc"
# 			)

# 			if last_child:
# 				new_index = int(last_child.split(".")[-1]) + 1
# 			else:
# 				new_index = 1

# 			self.task_no = f"{parent_task_no}.{new_index}"

# 	def update_subject(self):

# 		if not self.subject or not self.task_no:
# 			return

# 		subject = self.subject

# 		parts = subject.split(" - ", 1)

# 		# Remove old task number if already exists
# 		if parts[0].replace(".", "").isdigit():
# 			subject = parts[1] if len(parts) > 1 else ""

# 		self.subject = f"{self.task_no} - {subject}"

# 	@frappe.whitelist()
# 	def get_dept(self):
# 		if self.allocated_by:
# 			user = self.allocated_by
# 		else:
# 			user = frappe.session.user

# 		dept = frappe.db.get_value(
# 			"Employee",
# 			{"user_id": user},
# 			"department"
# 		)

# 		# Set only if department found
# 		if dept:
# 			abr=frappe.db.get_value("Department",dept,"custom_abbreviation")
# 			self.department = dept
# 			self.abbreviation=abr
		
# @frappe.whitelist()
# def get_task_assignees(task:str):

# 	assign = frappe.db.get_list(
# 		"ToDo",
# 		filters={"reference_name": task},
# 		fields=["allocated_to"]
# 	)

# 	assign_by = []
# 	users = []

# 	assigned = frappe.db.get_value(
# 		"SNM Task",
# 		task,
# 		"username"
# 	)

# 	if assigned:
# 		assign_by.append(assigned)

# 	if assign:

# 		for row in assign:

# 			full_name = frappe.db.get_value(
# 				"User",
# 				row.get("allocated_to"),
# 				"full_name"
# 			)

# 			if full_name:
# 				users.append(full_name)

# 	users_str = ", ".join(users)
# 	assign_by_str = ", ".join(assign_by)

# 	return users_str, assign_by_str


# @frappe.whitelist()
# def check_if_child_exists(name:str):

# 	child_tasks = frappe.get_all(
# 		"SNM Task",
# 		filters={"parent_task": name}
# 	)

# 	child_tasks = [
# 		get_link_to_form("SNM Task", task.name)
# 		for task in child_tasks
# 	]

# 	return child_tasks


# @frappe.whitelist()
# def get_children(
#     doctype: str,
#     parent: str,
#     task: str | None = None,
#     project: str | None = None,
#     is_root: bool = False,) -> list:
# 	filters = [["docstatus", "<", "2"]]

# 	if task:

# 		filters.append(["parent_task", "=", task])

# 	elif parent and not is_root:

# 		filters.append(["parent_task", "=", parent])

# 	else:

# 		from frappe.query_builder import Field, functions

# 		filters.append(
# 			functions.IfNull(Field("parent_task"), "") == ""
# 		)

# 	if project:
# 		filters.append(["project", "=", project])

# 	tasks = frappe.get_list(
# 		doctype,
# 		fields=[
# 			"name as value",
# 			"subject as title",
# 			"is_group as expandable"
# 		],
# 		filters=filters,
# 		order_by="name",
# 	)

# 	return tasks


# @frappe.whitelist()
# def add_node():

# 	from frappe.desk.treeview import make_tree_args

# 	args = frappe.form_dict

# 	args.update({
# 		"name_field": "subject"
# 	})

# 	args = make_tree_args(**args)

# 	if args.parent_task == "All Tasks" or args.parent_task == args.project:
# 		args.parent_task = None

# 	frappe.get_doc(args).insert()


# @frappe.whitelist()
# def add_multiple_tasks(data:str, parent:str):

# 	data = json.loads(data)

# 	new_doc = {
# 		"doctype": "SNM Task",
# 		"parent_task": parent if parent != "All Tasks" else ""
# 	}

# 	new_doc["project"] = frappe.db.get_value(
# 		"SNM Task",
# 		{"name": parent},
# 		"project"
# 	) or ""

# 	for d in data:

# 		if not d.get("subject"):
# 			continue

# 		new_doc["subject"] = d.get("subject")

# 		new_task = frappe.get_doc(new_doc)

# 		new_task.insert()


# def on_doctype_update():
# 	frappe.db.add_index("SNM Task", ["lft", "rgt"])


# def update_snm_task_whatsapp_numbers_from_todo(doc, method=None):
# 	if doc.reference_type != "SNM Task" or not doc.reference_name:
# 		return
# 	set_whatsapp_numbers_for_assigned_user(doc.reference_name, doc.allocated_to)
# def set_whatsapp_numbers_for_assigned_user(task, user):
# 	if not task or not user:
# 		return

# 	user_contact = frappe.db.get_value("User",user,["mobile_no", "phone"],as_dict=True,)
# 	numbers = []
# 	if user_contact:
# 		for fieldname in ("mobile_no", "phone"):
# 			number = (user_contact.get(fieldname) or "").strip()

# 			if number and number not in numbers:
# 				numbers.append(number)

# 	frappe.db.set_value(
# 		"SNM Task",
# 		task,
# 		"whatsapp_number",
# 		", ".join(numbers),
# 		update_modified=False,
# 	)


# def send_overdue_task_notifications():

#     user_tasks = {}

#     overdue_tasks = frappe.get_all(
#         "SNM Task",
#         filters={"status": "Overdue"},
#         fields=["name", "subject"]
#     )

#     for task in overdue_tasks:

#         todos = frappe.get_all(
#             "ToDo",
#             filters={
#                 "reference_type": "SNM Task",
#                 "reference_name": task.name,
#                 "allocated_to": ["is", "set"]
#             },
#             fields=["allocated_to"]
#         )

#         for todo in todos:

#             if todo.allocated_to not in user_tasks:
#                 user_tasks[todo.allocated_to] = []

#             user_tasks[todo.allocated_to].append(task)

#     for user, tasks in user_tasks.items():

#         rows = ""

#         for idx, task in enumerate(tasks, 1):

#             task_link = get_url_to_form("SNM Task", task.name)

#             rows += f"""
#             <tr>
#                 <td>{idx}</td>
#                 <td>
#                     <a href="{task_link}">
#                         {task.name}
#                     </a>
#                 </td>
#                 <td>{task.subject or ''}</td>
#             </tr>
#             """

#         message = f"""
#         <div style="font-family: Arial, sans-serif; max-width: 800px;">

#             <h2 style="color:#d9534f;">
#                 Overdue Task Notification
#             </h2>

#             <p>Hello,</p>

#             <p>
#                 You have <b>{len(tasks)}</b> overdue task(s) assigned to you.
#             </p>

#             <table
#                 border="1"
#                 cellpadding="8"
#                 cellspacing="0"
#                 width="100%"
#                 style="border-collapse:collapse;"
#             >
#                 <thead>
#                     <tr style="background-color:#f5f5f5;">
#                         <th>#</th>
#                         <th>Task</th>
#                         <th>Subject</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     {rows}
#                 </tbody>
#             </table>

#             <br>

#             <p>
#                 Please review and update these tasks.
#             </p>

#             <hr>

#             <p style="font-size:12px;color:gray;">
#                 This is an automated notification from ERPNext.
#             </p>

#         </div>
#         """

#         frappe.sendmail(
#             recipients=[user],
#             subject=f"{len(tasks)} Overdue Task(s) Assigned To You",
#             message=message,
#             delayed=False
#         )

#         frappe.logger().info(
#             f"Overdue notification sent to {user} for {len(tasks)} tasks"
#         )
# Copyright (c) 2026, Shivangi and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe import _, throw
from frappe.desk.form.assign_to import clear, close_all_assignments
from frappe.utils import get_link_to_form, get_url_to_form
from frappe.desk.form.assign_to import add as add_assignment


class ParentIsGroupError(frappe.ValidationError):
    pass


class SNMTask(Document):

    def validate(self):
        self.set_group_task()
        self.update_depends_on()
        self.validate_parent_is_group()
        self.validate_due_date()
        self.get_dept()
        self.update_description()
        self.update_snm_description()
        # self.update_child_description()
        self.update_subject()

    def on_update(self):
        self.update_child_description()

    def before_insert(self):
        self.get_task_no()

    def after_insert(self):
        
        self.assign_user()
        self.create_child_tasks()
        self.update_meet()

    def on_update(self):
        self.create_child_tasks()
        self.populate_depends_on()
        self.unassign_todo()
        # self.update_subject()

    # def assign_user(self):
    # 	for row in self.assigned_users:
    # 		if not row.user:
    # 			continue

    # 		exists = frappe.db.exists(
    # 			"ToDo",
    # 			{
    # 				"reference_type": self.doctype,
    # 				"reference_name": self.name,
    # 				"allocated_to": row.user,
    # 				"status": "Open",
    # 			},
    # 		)

    # 		if exists:
    # 			continue

    # 		todo = frappe.get_doc(
    # 			{
    # 				"doctype": "ToDo",
    # 				"allocated_to": row.user,
    # 				"reference_type": self.doctype,
    # 				"reference_name": self.name,
    # 				"description": self.subject or self.name,
    # 				"status": "Open",
    # 			}
    # 		)
    # 		todo.insert(ignore_permissions=True)
    def assign_user(self):
        current_users = [row.user for row in self.assigned_users if row.user]

        # Create ToDo for selected users
        for user in current_users:
            exists = frappe.db.exists(
                "ToDo",
                {
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "allocated_to": user,
                    "status": "Open",
                },
            )

            if exists:
                continue

            frappe.get_doc(
                {
                    "doctype": "ToDo",
                    "allocated_to": user,
                    "reference_type": self.doctype,
                    "reference_name": self.name,
                    "description": self.subject or self.name,
                    "status": "Open",
                }
            ).insert(ignore_permissions=True)

        # Remove ToDo if user removed from assigned_users
        existing_todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": self.doctype,
                "reference_name": self.name,
                "status": "Open",
            },
            fields=["name", "allocated_to"],
        )

        for todo in existing_todos:
            if todo.allocated_to not in current_users:
                frappe.delete_doc("ToDo", todo.name, ignore_permissions=True)

    def validate_due_date(self):
        if not self.due_date:
            return
        if not self.depends_on:
            return

        for row in self.depends_on:
            if row.due_date and self.due_date < row.due_date:
                throw(
                    _(
                        "Due Date of Task cannot be before Due Date of dependent Task {0}"
                    ).format(get_link_to_form("SNM Task", row.task))
                )

    def set_group_task(self):

        # Auto enable group if child rows exist
        if self.depends_on and not self.is_group:
            self.is_group = 1

    def validate_parent_is_group(self):

        if self.parent_task:

            if not frappe.db.get_value("SNM Task", self.parent_task, "is_group"):

                frappe.throw(
                    _("Parent Task {0} must be a Group Task").format(
                        get_link_to_form("SNM Task", self.parent_task)
                    ),
                    ParentIsGroupError,
                )

    def populate_depends_on(self):
        if self.parent_task and not self.created_from_parent:

            parent = frappe.get_doc("SNM Task", self.parent_task)
            existing_tasks = [row.task for row in parent.depends_on]

            if self.name not in existing_tasks:

                parent.append(
                    "depends_on",
                    {
                        "doctype": "Task Depends On",
                        "task": self.name,
                        "subject": self.subject,
                        "description": self.description,
                        "priority": self.priority,
                        "status": self.status,
                        "parent_task": self.parent_task,
                    },
                )

                parent.flags.ignore_child_creation = True

                parent.save(ignore_permissions=True)

    def unassign_todo(self):

        if self.status == "Completed":
            close_all_assignments(self.doctype, self.name)

        if self.status == "Cancelled":
            clear(self.doctype, self.name)

    def update_depends_on(self):

        depends_on_tasks = ""

        for d in self.depends_on:
            if not d.parent_task:
                d.parent_task = self.name

            if d.task and d.task not in depends_on_tasks:
                depends_on_tasks += d.task + ","

        self.depends_on_tasks = depends_on_tasks

    def create_child_tasks(self):

        # Prevent recursive save loop
        if self.flags.ignore_child_creation:
            return

        if not self.depends_on:
            return

        for row in self.depends_on:

            # Skip if already linked
            if row.task:
                continue

            child_task = frappe.get_doc(
                {
                    "doctype": "SNM Task",
                    "subject": row.subject,
                    "parent_task": self.name,
                    "allocated_by": frappe.session.user,
                    "status": row.status,
                    "priority": row.priority,
                    "created_from_parent": 1,
                    "start_date": row.start_date,
                    "due_date": row.due_date,
                    "description": row.description,
                    "created_by": row.user_id,
                }
            )

            child_task.flags.ignore_child_creation = True

            child_task.insert(ignore_permissions=True)

            # Update only current row
            row.db_set("task", child_task.name)
            if row.user:
                todo = frappe.new_doc("ToDo")
                todo.assigned_by = frappe.session.user
                todo.reference_type = "SNM Task"
                todo.reference_name = child_task.name
                todo.priority = child_task.priority
                todo.description = child_task.subject
                todo.date = child_task.due_date
                todo.allocated_to = row.user
                todo.status = "Open"
                todo.insert(ignore_permissions=True)

    def update_description(self):
        if not self.meeting:
            return
        if not self.has_value_changed("description"):
            return
        row = frappe.db.get_value(
            "Child Tasks", {"parent": self.meeting, "task": self.name}, "name"
        )
        frappe.db.set_value("Child Tasks", row, "description", self.description)

    def update_snm_description(self):
        if not self.parent_task:
            return
        if not self.has_value_changed("description"):
            return
        row = frappe.db.get_value(
            "Child Tasks", {"parent": self.parent_task, "task": self.name}, "name"
        )
        frappe.db.set_value("Child Tasks", row, "description", self.description)

    def update_child_description(self):
        if not self.depends_on:
            return
        for row in self.depends_on:
            if not row.task:
                return
            if row.has_value_changed("description"):
                frappe.db.set_value(
                    "Task Depends On",
                    {"name": row.name},
                    "description",
                    self.description,
                )

    def on_trash(self):

        if check_if_child_exists(self.name):

            throw(_("Child Task exists for this Task. You can not delete this Task."))

    def update_meet(self):
        if not self.meeting:
            return

        meet = frappe.get_doc("Meeting", self.meeting)

        if any(row.task == self.name for row in meet.tasks):
            return

        meet.append(
            "tasks",
            {
                "task": self.name,
                "subject": self.subject,
                "user": self.allocated_by,
                "status": self.status,
                "priority": self.priority,
                "start_date": self.start_date,
                "due_date": self.due_date,
                "parent_task": self.parent_task,
                "description": self.description,
                "is_meeting_task": self.is_meeting_task,
            },
        )

        meet.save(ignore_permissions=True)

    @frappe.whitelist()
    def get_task_no(self):

        if not self.parent_task:

            max_task = frappe.db.sql(
                """
				SELECT MAX(CAST(task_no AS UNSIGNED))
				FROM `tabSNM Task`
				WHERE parent_task IS NULL OR parent_task = ''
			""",
                as_list=True,
            )[0][0]

            if max_task:
                self.task_no = str(max_task + 1)
            else:
                self.task_no = "1"

        else:

            parent_task_no = frappe.db.get_value(
                "SNM Task", self.parent_task, "task_no"
            )

            last_child = frappe.db.get_value(
                "SNM Task",
                {"parent_task": self.parent_task, "task_no": ["is", "set"]},
                "task_no",
                order_by="creation desc",
            )

            if last_child:
                new_index = int(last_child.split(".")[-1]) + 1
            else:
                new_index = 1

            self.task_no = f"{parent_task_no}.{new_index}"

    def update_subject(self):

        if not self.subject or not self.task_no:
            return

        subject = self.subject

        parts = subject.split(" - ", 1)

        # Remove old task number if already exists
        if parts[0].replace(".", "").isdigit():
            subject = parts[1] if len(parts) > 1 else ""

        self.subject = f"{self.task_no} - {subject}"

    @frappe.whitelist()
    def get_dept(self):
        if self.allocated_by:
            user = self.allocated_by
        else:
            user = frappe.session.user

        dept = frappe.db.get_value("Employee", {"user_id": user}, "department")

        # Set only if department found
        if dept:
            abr = frappe.db.get_value("Department", dept, "custom_abbreviation")
            self.department = dept
            self.abbreviation = abr


@frappe.whitelist()
def get_task_assignees(task: str):

    assign = frappe.db.get_list(
        "ToDo", filters={"reference_name": task}, fields=["allocated_to"]
    )

    assign_by = []
    users = []

    assigned = frappe.db.get_value("SNM Task", task, "username")

    if assigned:
        assign_by.append(assigned)

    if assign:

        for row in assign:

            full_name = frappe.db.get_value(
                "User", row.get("allocated_to"), "full_name"
            )

            if full_name:
                users.append(full_name)

    users_str = ", ".join(users)
    assign_by_str = ", ".join(assign_by)

    return users_str, assign_by_str


@frappe.whitelist()
def check_if_child_exists(name: str):

    child_tasks = frappe.get_all("SNM Task", filters={"parent_task": name})

    child_tasks = [get_link_to_form("SNM Task", task.name) for task in child_tasks]

    return child_tasks


@frappe.whitelist()
def get_kanban_subtasks(parent_tasks: str | list[str]) -> dict:
    """Compatibility endpoint for older loaded SNM Task Kanban assets."""
    if not frappe.has_permission("SNM Task", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if isinstance(parent_tasks, str):
        parent_tasks = json.loads(parent_tasks or "[]")

    parent_tasks = list(dict.fromkeys(parent_tasks or []))
    if not parent_tasks:
        return {}

    grouped_tasks = {}
    parents_to_fetch = parent_tasks
    visited = set(parent_tasks)

    while parents_to_fetch:
        children = frappe.get_list(
            "SNM Task",
            filters={"parent_task": ["in", parents_to_fetch]},
            fields=[
                "name",
                "subject",
                "status",
                "priority",
                "due_date",
                "parent_task",
            ],
            order_by="task_no asc, creation asc",
            limit_page_length=0,
        )

        next_parents = []
        for child in children:
            grouped_tasks.setdefault(child.parent_task, []).append(child)
            if child.name not in visited:
                visited.add(child.name)
                next_parents.append(child.name)

        parents_to_fetch = next_parents

    return grouped_tasks


@frappe.whitelist()
def get_children(
    doctype: str,
    parent: str,
    task: str | None = None,
    project: str | None = None,
    is_root: bool = False,
) -> list:
    filters = [["docstatus", "<", "2"]]

    if task:

        filters.append(["parent_task", "=", task])

    elif parent and not is_root:

        filters.append(["parent_task", "=", parent])

    else:

        from frappe.query_builder import Field, functions

        filters.append(functions.IfNull(Field("parent_task"), "") == "")

    if project:
        filters.append(["project", "=", project])

    tasks = frappe.get_list(
        doctype,
        fields=["name as value", "subject as title", "is_group as expandable"],
        filters=filters,
        order_by="name",
    )

    return tasks


@frappe.whitelist()
def add_node():

    from frappe.desk.treeview import make_tree_args

    args = frappe.form_dict

    args.update({"name_field": "subject"})

    args = make_tree_args(**args)

    if args.parent_task == "All Tasks" or args.parent_task == args.project:
        args.parent_task = None

    frappe.get_doc(args).insert()


@frappe.whitelist()
def add_multiple_tasks(data: str, parent: str):

    data = json.loads(data)

    new_doc = {
        "doctype": "SNM Task",
        "parent_task": parent if parent != "All Tasks" else "",
    }

    new_doc["project"] = (
        frappe.db.get_value("SNM Task", {"name": parent}, "project") or ""
    )

    for d in data:

        if not d.get("subject"):
            continue

        new_doc["subject"] = d.get("subject")

        new_task = frappe.get_doc(new_doc)

        new_task.insert()


def on_doctype_update():
    frappe.db.add_index("SNM Task", ["lft", "rgt"])


def update_snm_task_whatsapp_numbers_from_todo(doc, method=None):
    if doc.reference_type != "SNM Task" or not doc.reference_name:
        return
    set_whatsapp_numbers_for_assigned_user(doc.reference_name, doc.allocated_to)


def set_whatsapp_numbers_for_assigned_user(task, user):
    if not task or not user:
        return

    user_contact = frappe.db.get_value(
        "User",
        user,
        ["mobile_no", "phone"],
        as_dict=True,
    )
    numbers = []
    if user_contact:
        for fieldname in ("mobile_no", "phone"):
            number = (user_contact.get(fieldname) or "").strip()

            if number and number not in numbers:
                numbers.append(number)

    frappe.db.set_value(
        "SNM Task",
        task,
        "whatsapp_number",
        ", ".join(numbers),
        update_modified=False,
    )


def send_overdue_task_notifications():

    user_tasks = {}

    overdue_tasks = frappe.get_all(
        "SNM Task", filters={"status": "Overdue"}, fields=["name", "subject"]
    )

    for task in overdue_tasks:

        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "SNM Task",
                "reference_name": task.name,
                "allocated_to": ["is", "set"],
            },
            fields=["allocated_to"],
        )

        for todo in todos:

            if todo.allocated_to not in user_tasks:
                user_tasks[todo.allocated_to] = []

            user_tasks[todo.allocated_to].append(task)

    for user, tasks in user_tasks.items():

        rows = ""

        for idx, task in enumerate(tasks, 1):

            task_link = get_url_to_form("SNM Task", task.name)

            rows += f"""
            <tr>
                <td>{idx}</td>
                <td>
                    <a href="{task_link}">
                        {task.name}
                    </a>
                </td>
                <td>{task.subject or ''}</td>
            </tr>
            """

        message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px;">

            <h2 style="color:#d9534f;">
                Overdue Task Notification
            </h2>

            <p>Hello,</p>

            <p>
                You have <b>{len(tasks)}</b> overdue task(s) assigned to you.
            </p>

            <table
                border="1"
                cellpadding="8"
                cellspacing="0"
                width="100%"
                style="border-collapse:collapse;"
            >
                <thead>
                    <tr style="background-color:#f5f5f5;">
                        <th>#</th>
                        <th>Task</th>
                        <th>Subject</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <br>

            <p>
                Please review and update these tasks.
            </p>

            <hr>

            <p style="font-size:12px;color:gray;">
                This is an automated notification from ERPNext.
            </p>

        </div>
        """

        frappe.sendmail(
            recipients=[user],
            subject=f"{len(tasks)} Overdue Task(s) Assigned To You",
            message=message,
            delayed=False,
        )

        frappe.logger().info(
            f"Overdue notification sent to {user} for {len(tasks)} tasks"
        )
