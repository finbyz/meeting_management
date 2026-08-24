// (function () {
// 	const DOCTYPE = "SNM Task";
// 	const PATCH_FLAG = "__meeting_management_snm_task_kanban_tree";

// 	function is_snm_task_kanban() {
// 		const route = frappe.get_route();
// 		return route[0] === "List" && route[1] === DOCTYPE && route[2] === "Kanban";
// 	}

// 	function patch_kanban_view() {
// 		if (!frappe.views?.KanbanView || frappe.views.KanbanView.prototype[PATCH_FLAG]) {
// 			return false;
// 		}

// 		const prototype = frappe.views.KanbanView.prototype;
// 		const set_fields = prototype.set_fields;
// 		const after_render = prototype.after_render;

// 		prototype.set_fields = function () {
// 			const result = set_fields.apply(this, arguments);

// 			if (this.doctype === DOCTYPE) {
// 				this._add_field("parent_task");
// 				this._add_field("task_no");
// 				this._add_field("status");
// 				this._add_field("priority");
// 				this._add_field("due_date");
// 			}

// 			return result;
// 		};

// 		prototype.after_render = function () {
// 			if (after_render) {
// 				after_render.apply(this, arguments);
// 			}

// 			if (this.doctype !== DOCTYPE || this.view_name !== "Kanban") {
// 				return;
// 			}

// 			render_nested_tasks(this);
// 		};

// 		prototype[PATCH_FLAG] = true;
// 		return true;
// 	}

// 	function render_nested_tasks(list_view) {
// 		add_styles();

// 		const grouped_tasks = get_visible_grouped_tasks(list_view);
// 		list_view.__snm_task_kanban_grouped_tasks = grouped_tasks;
// 		append_nested_tasks(list_view, grouped_tasks);
// 		observe_kanban_rerenders(list_view);
// 	}

// 	function get_visible_grouped_tasks(list_view) {
// 		const visible_tasks = list_view.data || [];
// 		const visible_tasks_by_name = Object.fromEntries(
// 			visible_tasks.map((task) => [task.name, task])
// 		);
// 		const column_field = list_view.board?.field_name;
// 		const grouped_tasks = {};

// 		visible_tasks.forEach((task) => {
// 			const parent_task = visible_tasks_by_name[task.parent_task];
// 			if (!parent_task) {
// 				return;
// 			}

// 			if (column_field && task[column_field] !== parent_task[column_field]) {
// 				return;
// 			}

// 			grouped_tasks[task.parent_task] = grouped_tasks[task.parent_task] || [];
// 			grouped_tasks[task.parent_task].push(task);
// 		});

// 		return grouped_tasks;
// 	}

// 	function append_nested_tasks(list_view, grouped_tasks) {
// 		const $result = list_view.$result;
// 		list_view.__snm_task_applying_tree = true;

// 		$result.find(".snm-kanban-tree").remove();
// 		$result.find(".snm-kanban-has-tree").removeClass("snm-kanban-has-tree");

// 		Object.keys(grouped_tasks).forEach((parent_name) => {
// 			const children = grouped_tasks[parent_name] || [];
// 			const $card = $result.find(
// 				`.kanban-card-wrapper[data-name="${encodeURIComponent(parent_name)}"]`
// 			);

// 			if (!$card.length || !children.length) {
// 				return;
// 			}

// 			get_descendant_names(grouped_tasks, parent_name).forEach((task_name) => {
// 				$result
// 					.find(`.kanban-card-wrapper[data-name="${encodeURIComponent(task_name)}"]`)
// 					.remove();
// 			});

// 			$card.addClass("snm-kanban-has-tree");
// 			$card.find(".kanban-title-area").append(render_tree(grouped_tasks, parent_name, 1));
// 		});

// 		bind_child_task_drag_drop(list_view);

// 		setTimeout(() => {
// 			list_view.__snm_task_applying_tree = false;
// 		}, 0);
// 	}

// 	function observe_kanban_rerenders(list_view) {
// 		const result = list_view.$result?.get(0);
// 		if (!result) {
// 			return;
// 		}

// 		if (list_view.__snm_task_kanban_observer) {
// 			list_view.__snm_task_kanban_observer.disconnect();
// 		}

// 		list_view.__snm_task_kanban_observer = new MutationObserver(() => {
// 			if (list_view.__snm_task_applying_tree) {
// 				return;
// 			}

// 			clearTimeout(list_view.__snm_task_kanban_observer_timer);
// 			list_view.__snm_task_kanban_observer_timer = setTimeout(() => {
// 				if (!is_snm_task_kanban() || cur_list !== list_view) {
// 					list_view.__snm_task_kanban_observer.disconnect();
// 					return;
// 				}

// 				append_nested_tasks(
// 					list_view,
// 					list_view.__snm_task_kanban_grouped_tasks || {}
// 				);
// 			}, 80);
// 		});

// 		list_view.__snm_task_kanban_observer.observe(result, {
// 			childList: true,
// 			subtree: true,
// 		});
// 	}

// 	function get_descendant_names(grouped_tasks, parent_name) {
// 		const descendants = [];

// 		(grouped_tasks[parent_name] || []).forEach((task) => {
// 			descendants.push(task.name);
// 			descendants.push(...get_descendant_names(grouped_tasks, task.name));
// 		});

// 		return descendants;
// 	}

// 	function render_tree(grouped_tasks, parent_name, level) {
// 		const children = grouped_tasks[parent_name] || [];
// 		if (!children.length) {
// 			return "";
// 		}

// 		const rows = children
// 			.map((task) => {
// 				const title = frappe.utils.escape_html(task.subject || task.name);
// 				const has_children = Boolean((grouped_tasks[task.name] || []).length);
// 				const form_link = frappe.utils.get_form_link(DOCTYPE, task.name);
// 				const draggable_attr = has_children
// 					? ""
// 					: `data-task-name="${frappe.utils.escape_html(task.name)}"`;
// 				const draggable_class = has_children ? "snm-kanban-tree-row-branch" : "snm-kanban-tree-row-draggable";

// 				return `
// 					<div class="snm-kanban-tree-node" data-task-name="${frappe.utils.escape_html(
// 						task.name
// 					)}" style="--snm-tree-level: ${level}">
// 						<div class="snm-kanban-tree-row ${draggable_class}" ${draggable_attr}>
// 							<span class="snm-kanban-tree-toggle">${has_children ? "⌄" : ""}</span>
// 							<a class="snm-kanban-tree-title" href="${form_link}" title="${title}">
// 								${title}
// 							</a>
// 							<a class="snm-kanban-tree-add" href="${form_link}" title="${__("Open")}">+</a>
// 						</div>
// 						${render_tree(grouped_tasks, task.name, level + 1)}
// 					</div>
// 				`;
// 			})
// 			.join("");

// 		return `<div class="snm-kanban-tree">${rows}</div>`;
// 	}

// 	function bind_child_task_drag_drop(list_view) {
// 		const $result = list_view.$result;
// 		const namespace = ".snmKanbanChildDrag";
// 		const $rows = $result.find(".snm-kanban-tree-row-draggable");

// 		$rows.off(namespace);
// 		$(document).off(namespace);

// 		$rows.on(
// 			`mousedown${namespace} touchstart${namespace} dragstart${namespace}`,
// 			function (event) {
// 				event.preventDefault();
// 				event.stopPropagation();
// 				event.originalEvent?.stopImmediatePropagation?.();
// 			}
// 		);

// 		$rows.on(`pointerdown${namespace}`, function (event) {
// 			const original_event = event.originalEvent;
// 			if (original_event.button !== undefined && original_event.button !== 0) {
// 				return;
// 			}

// 			event.preventDefault();
// 			event.stopPropagation();
// 			original_event.stopImmediatePropagation();

// 			const $row = $(this);
// 			const task_name = $(this).data("task-name");
// 			const source_column = $(this).closest(".kanban-column").data("column-value");
// 			const pointer_id = original_event.pointerId;
// 			const start_x = original_event.clientX;
// 			const start_y = original_event.clientY;
// 			const row_rect = this.getBoundingClientRect();
// 			let dragging = false;
// 			let $ghost = null;
// 			let $target_column = null;

// 			$row.addClass("snm-kanban-tree-dragging");
// 			this.setPointerCapture?.(pointer_id);

// 			function start_drag(current_event) {
// 				if (dragging) {
// 					return;
// 				}

// 				dragging = true;
// 				$ghost = $row
// 					.clone()
// 					.addClass("snm-kanban-tree-drag-ghost")
// 					.css({
// 						left: current_event.clientX - row_rect.width / 2,
// 						top: current_event.clientY - row_rect.height / 2,
// 						width: row_rect.width,
// 					})
// 					.appendTo(document.body);
// 			}

// 			function move_ghost(current_event) {
// 				if (!$ghost) {
// 					return;
// 				}

// 				$ghost.css({
// 					left: current_event.clientX - row_rect.width / 2,
// 					top: current_event.clientY - row_rect.height / 2,
// 				});
// 			}

// 			function set_target_column(current_event) {
// 				const element = document.elementFromPoint(current_event.clientX, current_event.clientY);
// 				const $column = $(element).closest(".kanban-column");

// 				if ($target_column?.get(0) === $column.get(0)) {
// 					return;
// 				}

// 				$result.find(".snm-kanban-child-drop-target").removeClass("snm-kanban-child-drop-target");
// 				$target_column = $column.length ? $column : null;
// 				$target_column?.addClass("snm-kanban-child-drop-target");
// 			}

// 			function on_pointer_move(move_event) {
// 				const pointer_event = move_event.originalEvent || move_event;
// 				move_event.preventDefault();
// 				move_event.stopPropagation();
// 				pointer_event.stopPropagation?.();

// 				const moved =
// 					Math.abs(pointer_event.clientX - start_x) > 4 ||
// 					Math.abs(pointer_event.clientY - start_y) > 4;

// 				if (moved) {
// 					start_drag(pointer_event);
// 				}

// 				if (dragging) {
// 					move_ghost(pointer_event);
// 					set_target_column(pointer_event);
// 				}
// 			}

// 			function on_pointer_up(up_event) {
// 				const pointer_event = up_event.originalEvent || up_event;
// 				up_event.preventDefault();
// 				up_event.stopPropagation();
// 				pointer_event.stopPropagation?.();

// 				$(document).off(`pointermove${namespace}`, on_pointer_move);
// 				$(document).off(`pointerup${namespace} pointercancel${namespace}`, on_pointer_up);

// 				set_target_column(pointer_event);

// 				$row.removeClass("snm-kanban-tree-dragging");
// 				$ghost?.remove();
// 				$result.find(".snm-kanban-child-drop-target").removeClass("snm-kanban-child-drop-target");

// 				if (!dragging || !$target_column?.length) {
// 					return;
// 				}

// 				const target_column = $target_column.data("column-value");
// 				if (!target_column || source_column === target_column) {
// 					return;
// 				}

// 				update_child_task_column(list_view, task_name, target_column);
// 			}

// 			$(document).on(`pointermove${namespace}`, on_pointer_move);
// 			$(document).on(`pointerup${namespace} pointercancel${namespace}`, on_pointer_up);
// 		});
// 	}

// 	function update_child_task_column(list_view, task_name, target_column) {
// 		const field_name = list_view.board?.field_name;
// 		if (!field_name) {
// 			return;
// 		}

// 		frappe.db
// 			.set_value(DOCTYPE, task_name, field_name, target_column)
// 			.then(() => {
// 				frappe.show_alert({
// 					message: __("Task moved to {0}", [__(target_column)]),
// 					indicator: "green",
// 				});

// 				const moved_task = (list_view.data || []).find((task) => task.name === task_name);
// 				if (moved_task && field_name) {
// 					moved_task[field_name] = target_column;
// 				}

// 				list_view.last_args = null;
// 				list_view.refresh();
// 			})
// 			.catch(() => {
// 				frappe.show_alert({
// 					message: __("Could not move task"),
// 					indicator: "red",
// 				});
// 			});
// 	}

// 	function add_styles() {
// 		if (document.getElementById("snm-task-kanban-tree-styles")) {
// 			return;
// 		}

// 		$(`<style id="snm-task-kanban-tree-styles">
// 			.snm-kanban-has-tree .kanban-card {
// 				overflow: visible;
// 			}

// 			.snm-kanban-has-tree .kanban-card-title::before {
// 				color: var(--text-muted);
// 				content: "⌄";
// 				display: inline-block;
// 				font-size: 13px;
// 				margin-right: 8px;
// 				vertical-align: 1px;
// 			}

// 			.snm-kanban-tree {
// 				margin-top: 8px;
// 			}

// 			.snm-kanban-tree-node {
// 				border-left: 1px solid var(--border-color);
// 				margin-left: calc((var(--snm-tree-level, 1) - 1) * 18px + 10px);
// 				padding: 0 0 0 12px;
// 				position: relative;
// 			}

// 			.snm-kanban-tree-node::before {
// 				background: var(--border-color);
// 				content: "";
// 				height: 1px;
// 				left: 0;
// 				position: absolute;
// 				top: 15px;
// 				width: 12px;
// 			}

// 			.snm-kanban-tree-row {
// 				align-items: center;
// 				display: grid;
// 				gap: 6px;
// 				grid-template-columns: 12px minmax(0, 1fr) 18px;
// 				min-height: 30px;
// 				padding: 4px 0;
// 			}

// 			.snm-kanban-tree-row-draggable {
// 				cursor: grab;
// 				touch-action: none;
// 				user-select: none;
// 			}

// 			.snm-kanban-tree-row-draggable:active {
// 				cursor: grabbing;
// 			}

// 			.snm-kanban-tree-row-branch {
// 				cursor: default;
// 			}

// 			.snm-kanban-tree-dragging {
// 				opacity: 0.55;
// 			}

// 			.snm-kanban-tree-drag-ghost {
// 				background: var(--kanban-card-bg);
// 				border: 1px solid var(--border-color);
// 				border-radius: 6px;
// 				box-shadow: var(--shadow-md);
// 				display: grid;
// 				gap: 6px;
// 				grid-template-columns: 12px minmax(0, 1fr) 18px;
// 				min-height: 30px;
// 				opacity: 0.95;
// 				padding: 4px 8px;
// 				pointer-events: none;
// 				position: fixed;
// 				z-index: 9999;
// 			}

// 			.snm-kanban-child-drop-target {
// 				outline: 2px dashed var(--primary);
// 				outline-offset: -6px;
// 			}

// 			.snm-kanban-tree-toggle {
// 				color: var(--text-muted);
// 				font-size: 13px;
// 				line-height: 1;
// 				text-align: center;
// 			}

// 			.snm-kanban-tree-title {
// 				color: var(--text-color);
// 				font-size: var(--text-sm);
// 				font-weight: 500;
// 				line-height: 1.3;
// 				overflow: hidden;
// 				text-overflow: ellipsis;
// 				white-space: nowrap;
// 			}

// 			.snm-kanban-tree-add {
// 				align-items: center;
// 				background: var(--bg-light-gray);
// 				border-radius: 50%;
// 				color: var(--text-muted);
// 				display: inline-flex;
// 				font-size: 13px;
// 				height: 18px;
// 				justify-content: center;
// 				line-height: 18px;
// 				text-decoration: none;
// 				width: 18px;
// 			}

// 			.snm-kanban-tree-add:hover {
// 				background: var(--gray-200);
// 				color: var(--text-color);
// 				text-decoration: none;
// 			}
// 		</style>`).appendTo(document.head);
// 	}

// 	function apply_my_task_filter() {
// 		setTimeout(() => {
// 			const route = frappe.get_route();

// 			if (
// 				route[0] === "List" &&
// 				route[1] === DOCTYPE &&
// 				route[2] === "Kanban" &&
// 				route[3] === "My Task"
// 			) {
// 				const interval = setInterval(() => {
// 					if (cur_list && cur_list.filter_area) {
// 						clearInterval(interval);

// 						const current_user = frappe.session.user;
// 						cur_list.filter_area.clear(false);
// 						cur_list.filter_area.add([
// 							[DOCTYPE, "_assign", "like", "%" + current_user + "%"],
// 							[DOCTYPE, "owner", "=", current_user],
// 						]);
// 						cur_list.refresh();
// 					}
// 				}, 500);
// 			}
// 		}, 300);
// 	}

// 	frappe.router.on("change", () => {
// 		patch_kanban_view();
// 		apply_my_task_filter();

// 		if (is_snm_task_kanban() && cur_list?.doctype === DOCTYPE) {
// 			setTimeout(() => cur_list.refresh(), 100);
// 		}
// 	});

// 	const patch_interval = setInterval(() => {
// 		const patched = patch_kanban_view();

// 		if (frappe.views?.KanbanView?.prototype[PATCH_FLAG]) {
// 			clearInterval(patch_interval);
// 		}

// 		if (patched && is_snm_task_kanban() && cur_list?.doctype === DOCTYPE) {
// 			setTimeout(() => cur_list.refresh(), 100);
// 		}
// 	}, 100);
// })();

frappe.router.on("change", () => {
    setTimeout(() => {
        let route = frappe.get_route();

        if (
            route[0] === "List" &&
            route[1] === "SNM Task" &&
            route[2] === "Kanban"
        ) {
            let interval = setInterval(() => {
                if (cur_list && cur_list.filter_area) {
                    clearInterval(interval);

                    let current_user = frappe.session.user;

                    cur_list.filter_area.clear(false);

                    // My Task Kanban = Assigned To filter
                    if (route[3] === "My Task") {
                        cur_list.filter_area.add([
                            [
                                "SNM Task",
                                "_assign",
                                "like",
                                "%" + current_user + "%"
                            ]
                        ]);
                    }

                    // All Task Kanban = Created By filter
                    if (route[3] === "All Task") {
                        cur_list.filter_area.add([
                            [
                                "SNM Task",
                                "owner",
                                "=",
                                current_user
                            ]
                        ]);
                    }

                    cur_list.refresh();
                }
            }, 500);
        }
    }, 300);
});
