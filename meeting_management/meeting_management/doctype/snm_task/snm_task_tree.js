frappe.treeview_settings["SNM Task"] = {
	get_tree_nodes: "meeting_management.meeting_management.doctype.snm_task.snm_task.get_children",
	add_tree_node: "meeting_management.meeting_management.doctype.snm_task.snm_task.add_node",
	breadcrumb: "Meeting Management",
	get_tree_root: false,
	root_label: "SNM Task",
	ignore_fields: ["parent_task"],

	fields: [
		{
			fieldtype: "Check",
			fieldname: "is_group",
			label: __("Has Sub Task"),
			description: __("Further sub-groups can only be created under records marked as 'Group'")
		},
		{
			fieldtype: "Link",
			fieldname: "parent_task",
			label: __("Parent Task"),	
			options: "SNM Task",
		},
		{
			fieldtype: "Link",
			fieldname: "allocated_by",
			label: __("Allocated By"),
			options: "User",
			default: frappe.session.user
		}
	],

	onload: function (me) {

		frappe.treeview_settings["SNM Task"].page = {};
		$.extend(frappe.treeview_settings["SNM Task"].page, me.page);

		me.make_tree();

		function inject_assignees(task_name) {
			if (!task_name) return;

			const $label = $(`.tree .tree-link[data-label="${task_name}"]`);
			if (!$label.length) return;

			const $li = $label.closest("li");
			if (!$li.length) return;

			// Remove old assignees
			$li.find(".task-assignees").remove();

			// 🔥 Create flex row wrapper (if not already)
			if (!$label.parent().hasClass("tree-row-flex")) {
				const $row = $("<div class='tree-row-flex'></div>");

				$row.css({
					display: "flex",
					justifyContent: "space-between",
					alignItems: "center",
					width: "100%"
				});

				$label.wrap($row);
			}

			// Ensure label behaves correctly
			$label.css({
				flex: "1",
				minWidth: "0",
				overflow: "hidden",
				textOverflow: "ellipsis",
				whiteSpace: "nowrap"
			});

			frappe.call({
				method: "meeting_management.meeting_management.doctype.snm_task.snm_task.get_task_assignees",
				args: { task: task_name },

				callback: function (r) {

					const assignee_text =
						(r.message && r.message[0] ? r.message[0] : "") +
						(r.message && r.message[1] ? "/" + r.message[1] : "");

					const $assignees = $(`
						<span class="task-assignees"
							style="
								font-size: 11px;
								color: #6c757d;
								white-space: nowrap;
								margin-left: 10px;
							">
							${assignee_text}
						</span>
					`);

					// Append to flex row (right side automatically)
					$label.parent().append($assignees);
				}
			});
		}

		// Initial load
		setTimeout(() => {
			Object.values(me.tree.nodes || {}).forEach(node => {
				if (node?.data?.value) {
					inject_assignees(node.data.value);
				}
			});
		}, 800);

		// On expand/click
		me.page.main.on("click", ".tree-link", function () {
			setTimeout(() => {
				Object.values(me.tree.nodes || {}).forEach(node => {
					if (node?.data?.value) {
						inject_assignees(node.data.value);
					}
				});
			}, 400);
		});
	}
};