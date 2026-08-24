frappe.pages['meeting-management-dashboard'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Meeting Management Dashboard"),
		single_column: true,
	});

	new MeetingManagementDashboardPage(wrapper, page);
};

class MeetingManagementDashboardPage {
	constructor(wrapper, page) {
		this.wrapper = $(wrapper);
		this.page = page;
		this.chartInstances = {};
		this.autoRefreshMs = 15000;
		this.recentTaskInitialLimit = 5;
		this.recentTaskVisibleCount = this.recentTaskInitialLimit;
		this.inject_styles();
		this.render();
		this.bind_actions();
		this.refresh();
		this.start_auto_refresh();
	}

	inject_styles() {
		if ($("#meeting-management-dashboard-style").length) return;

		$("head").append(`
			<style id="meeting-management-dashboard-style">
				.meeting-management-dashboard {
					--mm-bg: #f4f1e8;
					--mm-card: #fffdf8;
					--mm-border: rgba(41,52,67,.18);
					--mm-border-strong: rgba(41,52,67,.26);
					--mm-ink: #202935;
					--mm-muted: #65707f;
					--mm-primary: #215f86;
					--mm-accent: #cc8840;
					--mm-soft: #e6edf3;
					--mm-warm: #f8e7d0;
					padding: 16px 24px 24px 24px;
					font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
				}

				.meeting-management-dashboard .mm-hero,
				.meeting-management-dashboard .mm-card {
					background: var(--mm-card);
					border: 1px solid var(--mm-border-strong);
					border-radius: 22px;
					box-shadow: 0 14px 34px rgba(32,41,53,.06);
					position: relative;
					overflow: hidden;
				}

				.meeting-management-dashboard .mm-hero::before,
				.meeting-management-dashboard .mm-card::before {
					content: "";
					position: absolute;
					inset: -35% auto auto -10%;
					width: 45%;
					height: 70%;
					background: radial-gradient(circle, rgba(255,255,255,.16), transparent 70%);
					opacity: .75;
					pointer-events: none;
					animation: mm-drift 20s ease-in-out infinite alternate;
					z-index: 0;
				}

				.meeting-management-dashboard .mm-hero::after,
				.meeting-management-dashboard .mm-card::after {
					content: "";
					position: absolute;
					inset: auto -12% -42% auto;
					width: 34%;
					height: 58%;
					background: radial-gradient(circle, rgba(33,95,134,.14), transparent 72%);
					opacity: .55;
					pointer-events: none;
					animation: mm-drift-reverse 24s ease-in-out infinite alternate;
					z-index: 1;
				}

				.meeting-management-dashboard .mm-hero > *,
				.meeting-management-dashboard .mm-card > * {
					position: relative;
					z-index: 1;
				}

				.meeting-management-dashboard .mm-hero {
					overflow: visible !important;
					padding: 24px 28px;
					margin-bottom: 24px;
					background: radial-gradient(circle at top right, rgba(204,136,64,.20), transparent 24%),
						linear-gradient(135deg, #fffdf8 0%, #f0ebe0 55%, #eaf1f6 100%);
				}

				.meeting-management-dashboard .mm-kicker {
					font-size: 12px;
					text-transform: uppercase;
					letter-spacing: .08em;
					color: var(--mm-accent);
					font-weight: 700;
				}

				.meeting-management-dashboard .mm-title {
					margin-top: 4px;
					font-size: 24px;
					line-height: 1.08;
					font-weight: 800;
					color: var(--mm-ink);
				}

				.meeting-management-dashboard .mm-note {
					margin-top: 6px;
					max-width: 760px;
					color: var(--mm-muted);
					font-size: 13px;
				}

				.meeting-management-dashboard .mm-toolbar {
					display: flex;
					gap: 16px;
					flex-wrap: wrap;
					margin-top: 16px;
				}

				.meeting-management-dashboard .mm-toolbar .btn {
					border-radius: 10px;
					padding: 6px 12px;
					min-height: 32px;
				}

				.meeting-management-dashboard .mm-filters {
					display: grid;
					grid-template-columns: repeat(3, minmax(170px, 1fr));
					gap: 12px;
					margin-top: 12px;
					align-items: end;
				}

				.meeting-management-dashboard .mm-filters .frappe-control {
					margin-bottom: 0;
				}

				.meeting-management-dashboard .mm-filters .form-control,
				.meeting-management-dashboard .mm-filters .awesomplete input {
					min-height: 34px;
					height: 34px;
					border-radius: 10px;
					border: 1px solid rgba(41,52,67,.14);
					padding: 6px 10px;
				}

				.meeting-management-dashboard .mm-filters .control-label {
					color: var(--mm-muted);
					font-size: 11px;
					font-weight: 600;
					margin-bottom: 4px;
				}

				.meeting-management-dashboard .mm-summary {
					display: grid;
					grid-template-columns: repeat(6, minmax(0, 1fr));
					gap: 24px;
					margin-bottom: 36px;
				}

				.meeting-management-dashboard .mm-stat {
					padding: 16px;
					border-radius: 18px;
					min-height: 112px;
					position: relative;
					overflow: hidden;
					border: 1px solid rgba(255,255,255,.38);
					transform-origin: center;
					animation: mm-stat-breathe 9s ease-in-out infinite;
				}

				.meeting-management-dashboard .mm-stat::after {
					content: "";
					position: absolute;
					inset: auto -16px -24px auto;
					width: 72px;
					height: 72px;
					border-radius: 50%;
					background: rgba(255,255,255,.16);
					animation: mm-float 18s ease-in-out infinite alternate;
				}

				.meeting-management-dashboard .mm-stat::before {
					content: "";
					position: absolute;
					inset: -22% auto auto -14%;
					width: 88px;
					height: 88px;
					border-radius: 50%;
					background: rgba(255,255,255,.09);
					animation: mm-float 24s ease-in-out infinite alternate-reverse;
				}

				.meeting-management-dashboard .mm-stat.is-updating {
					animation: mm-stat-breathe 9s ease-in-out infinite, mm-stat-glow .9s ease;
				}

				.meeting-management-dashboard .mm-stat.primary { background: linear-gradient(135deg, #215f86, #3b86b0); color: #fff; }
				.meeting-management-dashboard .mm-stat.accent { background: linear-gradient(135deg, #bf7b34, #ddaa68); color: #fff; }
				.meeting-management-dashboard .mm-stat.warm { background: linear-gradient(135deg, #ecd8bc, #dcc39b); color: #372514; }
				.meeting-management-dashboard .mm-stat.ink { background: linear-gradient(135deg, #d6dde4, #bdc8d2); color: #1f2b36; }
				.meeting-management-dashboard .mm-stat.soft { background: linear-gradient(135deg, #dde8ef, #c8d8e2); color: #20303d; }
				.meeting-management-dashboard .mm-stat.success { background: linear-gradient(135deg, #d3e3dc, #bad1c7); color: #203228; }

				.meeting-management-dashboard .mm-stat-label {
					font-size: 11px;
					text-transform: uppercase;
					letter-spacing: .06em;
					opacity: .82;
				}

				.meeting-management-dashboard .mm-stat-value {
					margin-top: 10px;
					font-size: 28px;
					font-weight: 800;
					line-height: 1;
					transform-origin: left center;
				}

				.meeting-management-dashboard .mm-stat-value.is-updating {
					animation: mm-value-pop .55s cubic-bezier(.2,.9,.28,1);
				}

				.meeting-management-dashboard .mm-stat-foot {
					margin-top: 8px;
					font-size: 12px;
					opacity: .82;
				}

				.meeting-management-dashboard .mm-grid {
					display: grid;
					grid-template-columns: repeat(2, minmax(0, 1fr));
					gap: 24px;
					margin-bottom: 24px;
				}

				.meeting-management-dashboard .mm-card {
					padding: 20px;
				}

				.meeting-management-dashboard .mm-card-head {
					display: flex;
					justify-content: space-between;
					gap: 12px;
					align-items: flex-start;
					margin-bottom: 20px;
					padding-bottom: 12px;
					border-bottom: 1px solid var(--mm-border);
				}

				.meeting-management-dashboard .mm-card-title {
					font-size: 18px;
					font-weight: 800;
					color: var(--mm-ink);
				}

				.meeting-management-dashboard .mm-card-note {
					font-size: 12px;
					color: var(--mm-muted);
				}

				.meeting-management-dashboard .mm-chart {
					min-height: 260px;
				}

				.meeting-management-dashboard .mm-bottom {
					display: grid;
					grid-template-columns: 1fr 1.15fr;
					gap: 24px;
					margin-bottom: 24px;
				}

				.meeting-management-dashboard .mm-table-wrap {
					border: 1px solid var(--mm-border-strong);
					border-radius: 16px;
					overflow: auto;
				}

				.meeting-management-dashboard .mm-table-wrap table {
					margin-bottom: 0;
				}

				.meeting-management-dashboard .mm-table-footer {
					display: flex;
					justify-content: space-between;
					align-items: center;
					gap: 12px;
					margin-top: 12px;
					color: var(--mm-muted);
					font-size: 12px;
				}

				.meeting-management-dashboard .mm-show-more {
					border-radius: 10px;
					padding: 6px 12px;
					min-height: 32px;
				}

				.meeting-management-dashboard .mm-table-wrap thead th {
					background: #f5eee3;
					color: var(--mm-muted);
					font-size: 12px;
					white-space: nowrap;
				}

				.meeting-management-dashboard .mm-table-wrap tbody td {
					vertical-align: middle;
				}

				.meeting-management-dashboard .mm-pill {
					display: inline-flex;
					align-items: center;
					gap: 6px;
					padding: 5px 10px;
					border-radius: 999px;
					font-size: 11px;
					font-weight: 700;
					background: #ebf2f7;
					color: var(--mm-primary);
				}

				.meeting-management-dashboard .mm-pill.status-open { background: #fef3c7; color: #b45309; }
				.meeting-management-dashboard .mm-pill.status-working { background: #e0f2fe; color: #0369a1; }
				.meeting-management-dashboard .mm-pill.status-overdue { background: #ffe4e6; color: #be123c; }
				.meeting-management-dashboard .mm-pill.status-completed { background: #dcfce7; color: #15803d; }

				.meeting-management-dashboard .mm-empty {
					min-height: 200px;
					display: flex;
					align-items: center;
					justify-content: center;
					text-align: center;
					color: var(--mm-muted);
					border: 1px dashed rgba(41,52,67,.14);
					border-radius: 16px;
				}

				.meeting-management-dashboard .mm-chart .mm-empty {
					min-height: 240px;
				}

				.meeting-management-dashboard .mm-chart svg text {
					fill: var(--mm-muted) !important;
				}

				.meeting-management-dashboard .mm-chart svg .x-axis line,
				.meeting-management-dashboard .mm-chart svg .y-axis line,
				.meeting-management-dashboard .mm-chart svg .guide-line,
				.meeting-management-dashboard .mm-chart svg .domain {
					stroke: rgba(101,112,127,.24) !important;
				}

				[data-theme="dark"] .meeting-management-dashboard {
					--mm-card: #171d22;
					--mm-border: rgba(208,185,150,.16);
					--mm-border-strong: rgba(208,185,150,.26);
					--mm-ink: #f5eee3;
					--mm-muted: #b7ab97;
					--mm-primary: #4c8fba;
					--mm-accent: #dd9a55;
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-hero {
					background: radial-gradient(circle at top right, rgba(221,154,85,.14), transparent 24%),
						linear-gradient(135deg, #171c21 0%, #1f1b17 50%, #15212a 100%);
					box-shadow: 0 18px 42px rgba(0,0,0,.28);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-card {
					background: linear-gradient(180deg, rgba(26,31,35,.96), rgba(18,22,25,.96));
					box-shadow: 0 16px 34px rgba(0,0,0,.24);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-stat.warm { background: linear-gradient(135deg, #5e472b, #775a35); color: #f7ead8; }
				[data-theme="dark"] .meeting-management-dashboard .mm-stat.ink { background: linear-gradient(135deg, #364753, #4b6272); color: #eef4f7; }
				[data-theme="dark"] .meeting-management-dashboard .mm-stat.soft { background: linear-gradient(135deg, #23323b, #31505d); color: #e0edf2; }
				[data-theme="dark"] .meeting-management-dashboard .mm-stat.success { background: linear-gradient(135deg, #22362d, #2f4d40); color: #e3f2ea; }

				[data-theme="dark"] .meeting-management-dashboard .mm-note,
				[data-theme="dark"] .meeting-management-dashboard .mm-card-note,
				[data-theme="dark"] .meeting-management-dashboard .mm-stat-foot,
				[data-theme="dark"] .meeting-management-dashboard .mm-stat-label {
					color: var(--mm-muted);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-filters .form-control,
				[data-theme="dark"] .meeting-management-dashboard .mm-filters .awesomplete input {
					background: #101418;
					color: var(--mm-ink);
					border-color: rgba(208,185,150,.14);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-toolbar .btn-default {
					background: #20262b;
					border-color: rgba(208,185,150,.12);
					color: var(--mm-ink);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-toolbar .btn-primary {
					background: linear-gradient(135deg, #28658c, #4187b1);
					border-color: transparent;
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-table-wrap thead th {
					background: #1d2328;
					color: #c8baa4;
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-table-wrap tbody td {
					color: #e8dcc9;
					border-top-color: rgba(208,185,150,.08);
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-pill {
					background: #17303f;
					color: #94c6e7;
				}

				[data-theme="dark"] .meeting-management-dashboard .mm-empty {
					border-color: rgba(208,185,150,.12);
					color: var(--mm-muted);
					background: rgba(255,255,255,.01);
				}

				@keyframes mm-drift { from { transform: translate3d(0, 0, 0) scale(1); opacity: .45; } to { transform: translate3d(18px, 12px, 0) scale(1.08); opacity: .72; } }
				@keyframes mm-drift-reverse { from { transform: translate3d(0, 0, 0) scale(1); opacity: .3; } to { transform: translate3d(-16px, -10px, 0) scale(1.06); opacity: .55; } }
				@keyframes mm-float { from { transform: translate3d(0, 0, 0); } to { transform: translate3d(10px, -8px, 0); } }
				@keyframes mm-stat-breathe { 0% { transform: translate3d(0, 0, 0) scale(1); } 50% { transform: translate3d(0, -2px, 0) scale(1.01); } 100% { transform: translate3d(0, 0, 0) scale(1); } }
				@keyframes mm-stat-glow { 0% { box-shadow: 0 14px 34px rgba(32,41,53,.06); } 45% { box-shadow: 0 18px 38px rgba(33,95,134,.16); } 100% { box-shadow: 0 14px 34px rgba(32,41,53,.06); } }
				@keyframes mm-value-pop { 0% { transform: translate3d(0, 4px, 0) scale(.96); opacity: .6; } 55% { transform: translate3d(0, -2px, 0) scale(1.06); opacity: 1; } 100% { transform: translate3d(0, 0, 0) scale(1); opacity: 1; } }

				@media (max-width: 1200px) {
					.meeting-management-dashboard .mm-summary { grid-template-columns: repeat(3, minmax(0, 1fr)); }
				}

				@media (max-width: 991px) {
					.meeting-management-dashboard .mm-grid,
					.meeting-management-dashboard .mm-bottom,
					.meeting-management-dashboard .mm-filters,
					.meeting-management-dashboard .mm-summary {
						grid-template-columns: 1fr;
					}
				}
			</style>
		`);
	}

	render() {
		this.body = $('<div class="meeting-management-dashboard"></div>').appendTo(this.page.body);
		this.body.html(`
			<div class="mm-hero">
				<div class="mm-kicker">${__("Meeting & Task Command Center")}</div>
				<div class="mm-title">${__("Meeting Management Dashboard")}</div>
				<div class="mm-note">${__("Monitor tasks, priority loads, calendar events, and live items with the same analytics-first layout used on the transportation dashboard.")}</div>
				<div class="mm-toolbar">
					<button class="btn btn-primary mm-refresh">${__("Refresh")}</button>
					<button class="btn btn-default mm-kanban">${__("Kanban View")}</button>
					<button class="btn btn-default mm-calendar">${__("Task Calendar")}</button>
					<button class="btn btn-default mm-tree">${__("Task Tree")}</button>
					<button class="btn btn-default mm-report">${__("Task Report")}</button>
					<button class="btn btn-default mm-meet-calendar">${__("Meeting Calendar")}</button>
				</div>
			</div>
			<div class="mm-summary"></div>
			<div class="mm-grid">
				<div class="mm-card">
					<div class="mm-card-head">
						<div>
							<div class="mm-card-title">${__("Open Tasks x Total Tasks")}</div>
							<div class="mm-card-note mm-range-note"></div>
						</div>
					</div>
					<div class="mm-chart mm-chart-status"></div>
				</div>
				<div class="mm-card">
					<div class="mm-card-head">
						<div>
							<div class="mm-card-title">${__("Task Priorities")}</div>
							<div class="mm-card-note">${__("Breakdown of tasks based on selected priority filters.")}</div>
						</div>
					</div>
					<div class="mm-chart mm-chart-priority"></div>
				</div>
			</div>
			<div class="mm-bottom">
				<div class="mm-card">
					<div class="mm-card-head">
						<div>
							<div class="mm-card-title">${__("Recent Tasks")}</div>
							<div class="mm-card-note">${__("Latest added tasks with their current execution status.")}</div>
						</div>
					</div>
					<div class="mm-tasks-table"></div>
				</div>
				<div class="mm-card">
					<div class="mm-card-head">
						<div>
							<div class="mm-card-title">${__("Upcoming / Recent Events")}</div>
							<div class="mm-card-note">${__("Recent schedules and event details logged in meeting management.")}</div>
						</div>
					</div>
					<div class="mm-events-table"></div>
				</div>
			</div>
		`);

		this.$summary = this.body.find(".mm-summary");
		this.$rangeNote = this.body.find(".mm-range-note");
		this.$tasksTable = this.body.find(".mm-tasks-table");
		this.$eventsTable = this.body.find(".mm-events-table");
	}

	bind_actions() {
		this.body.find(".mm-refresh").on("click", () => this.refresh());
		this.body.find(".mm-kanban").on("click", () => frappe.set_route("List", "SNM Task", "Kanban"));
		this.body.find(".mm-calendar").on("click", () => frappe.set_route("List", "SNM Task", "Calendar"));
		this.body.find(".mm-tree").on("click", () => frappe.set_route("Tree", "SNM Task"));
		this.body.find(".mm-report").on("click", () => frappe.set_route("List", "SNM Task", "Report"));
		this.body.find(".mm-meet-calendar").on("click", () => frappe.set_route("List", "Event", "Calendar"));
	}

	start_auto_refresh() {
		if (window.meetingDashboardAutoRefresh) {
			clearInterval(window.meetingDashboardAutoRefresh);
		}

		window.meetingDashboardAutoRefresh = setInterval(() => {
			if (frappe.get_route_str() === "meeting-management-dashboard") {
				this.refresh(true);
			}
		}, this.autoRefreshMs);
	}

	async refresh(isAutoRefresh = false) {
		const filters = {};
		const response = await frappe.call({
			method: "meeting_management.meeting_management.page.meeting_management_dashboard.meeting_management_dashboard.get_dashboard_data",
			freeze: !isAutoRefresh,
			freeze_message: __("Loading meeting analytics..."),
		});

		const data = response.message || {};
		this.currentData = data;

		this.render_summary(this.build_summary_cards(data));

		if (!isAutoRefresh) {
			this.recentTaskVisibleCount = this.recentTaskInitialLimit;
			this.render_charts(data, filters);
			this.render_tables(data, filters);
		}
	}

	build_summary_cards(data) {
		const stats = data.stats || {};
		return [
			{ label: __("Overdue Tasks"), value: stats.overdue_tasks || 0, tone: "accent", foot: __("Needs attention"), status: "Overdue" },
			{ label: __("To Do Tasks"), value: stats.total_tasks || 0, tone: "primary", foot: __("Pending completion"), status: "Open" },
			{ label: __("WIP Tasks"), value: stats.working_tasks || 0, tone: "soft", foot: __("In progress"), status: "Working" },
			{ label: __("Completed Tasks"), value: stats.completed_tasks || 0, tone: "success", foot: __("Successfully done"), status: "Completed" },
			{ label: __("Total Events"), value: stats.total_events || 0, tone: "ink", foot: __("Meetings scheduled"), doctype: "Event" },
			{ label: __("Total Tasks"), value: stats.all_tasks || 0, tone: "warm", foot: __("All tasks created"), doctype: "SNM Task" },
		];
	}

	render_summary(cards) {
		if (!cards.length) {
			this.$summary.html(`<div class="mm-card mm-empty">${__("No summary data available.")}</div>`);
			this.summaryCards = null;
			return;
		}

		if (!this.summaryCards || this.summaryCards.length !== cards.length) {
			this.summaryCards = [];
			this.$summary.empty();

			cards.forEach(() => {
				const $card = $(`
					<div class="mm-stat">
						<div class="mm-stat-label"></div>
						<div class="mm-stat-value"></div>
						<div class="mm-stat-foot"></div>
					</div>
				`);
				this.$summary.append($card);
				this.summaryCards.push($card);
			});
		}

		cards.forEach((card, index) => {
			const $card = this.summaryCards[index];
			const nextValue = card.value.toLocaleString();
			const $value = $card.find(".mm-stat-value");
			const valueChanged = $value.text() !== nextValue;

			$card.attr("class", `mm-stat ${frappe.utils.escape_html(card.tone || "soft")}`);
			$card.find(".mm-stat-label").text(card.label || "");
			$value.text(nextValue);
			$card.find(".mm-stat-foot").text(card.foot || "");
			$card.css("cursor", "pointer");

			$card.off("click").on("click", () => {
				if (card.doctype) {
					frappe.set_route("List", card.doctype);
				} else if (card.status) {
					frappe.set_route("List", "SNM Task", { status: card.status });
				}
			});

			if (valueChanged) {
				$card.addClass("is-updating");
				$value.removeClass("is-updating");
				void $value[0].offsetWidth;
				$value.addClass("is-updating");
				setTimeout(() => {
					$card.removeClass("is-updating");
					$value.removeClass("is-updating");
				}, 900);
			}
		});
	}

	render_charts(data, filters) {
		// Chart 1: Open Tasks x Total Tasks (grouped by status)
		const statusLabels = [];
		const statusValues = [];
		(data.status_chart || []).forEach(item => {
			if (item.status) {
				statusLabels.push(item.status);
				statusValues.push(item.count || 0);
			}
		});

		this.render_chart("status", this.body.find(".mm-chart-status")[0], {
			type: "donut",
			labels: statusLabels,
			values: statusValues,
			colors: ["#215f86", "#cc8840", "#bf7b34", "#3f8f6b", "#718096"]
		});

		// Chart 2: Task Priorities
		const priorityLabels = [];
		const priorityValues = [];
		(data.priority_chart || []).forEach(item => {
			if (item.priority) {
				priorityLabels.push(item.priority);
				priorityValues.push(item.count || 0);
			}
		});

		this.render_chart("priority", this.body.find(".mm-chart-priority")[0], {
			type: "pie",
			labels: priorityLabels,
			values: priorityValues,
			colors: ["#bf7b34", "#cc8840", "#215f86", "#3f8f6b"]
		});
	}

	render_chart(key, container, chartData) {
		if (!container) return;
		if (this.chartInstances[key]) {
			this.chartInstances[key].destroy();
			this.chartInstances[key] = null;
		}

		const values = chartData ? (chartData.values || []) : [];
		const hasData = values.some((value) => Number(value));

		if (!chartData || !(chartData.labels || []).length || !hasData) {
			container.innerHTML = `<div class="mm-empty">${__("No chart data found for the current filters.")}</div>`;
			return;
		}

		container.innerHTML = "";
		try {
			this.chartInstances[key] = new frappe.Chart(container, {
				type: chartData.type || "bar",
				height: 260,
				colors: chartData.colors || ["#215f86"],
				data: {
					labels: chartData.labels,
					datasets: [{ values }],
				},
				lineOptions: { hideDots: 1, regionFill: 1 },
				barOptions: { spaceRatio: 0.35 }
			});
		} catch (error) {
			console.error("Dashboard chart render failed:", key, error);
			container.innerHTML = `<div class="mm-empty">${__("Chart could not be loaded.")}</div>`;
		}
	}

	render_tables(data, filters) {
		// Table 1: Recent Tasks with Filter Support
		let filteredTasks = data.tasks || [];
		if (filters.priority) {
			filteredTasks = filteredTasks.filter(t => t.priority === filters.priority);
		}
		if (filters.status) {
			filteredTasks = filteredTasks.filter(t => t.status === filters.status);
		}
		if (filters.search) {
			const s = filters.search.toLowerCase();
			filteredTasks = filteredTasks.filter(t => 
				(t.name || '').toLowerCase().includes(s) ||
				(t.subject || '').toLowerCase().includes(s)
			);
		}

		if (!filteredTasks.length) {
			this.$tasksTable.html(`<div class="mm-empty">${__("No matching tasks found.")}</div>`);
		} else {
			const visibleTasks = filteredTasks.slice(0, this.recentTaskVisibleCount);
			const hasMoreTasks = filteredTasks.length > visibleTasks.length;

			this.$tasksTable.html(`
				<div class="mm-table-wrap">
					<table class="table table-hover">
						<thead>
							<tr>
								<th>${__("Task Description")}</th>
								<th>${__("Status")}</th>
								<th>${__("Priority")}</th>
								<th>${__("Due Date")}</th>
							</tr>
						</thead>
						<tbody>
							${visibleTasks.map((t) => {
								const statusClass = `status-${(t.status || '').toLowerCase()}`;
								const formattedDate = t.due_date ? frappe.datetime.str_to_user(t.due_date) : '-';
								return `
									<tr class="mm-row-link" data-doctype="SNM Task" data-name="${frappe.utils.escape_html(t.name)}">
										<td><strong>${frappe.utils.escape_html(t.subject || t.name)}</strong></td>
										<td><span class="mm-pill ${statusClass}">${frappe.utils.escape_html(t.status || 'Open')}</span></td>
										<td><span class="mm-pill">${frappe.utils.escape_html(t.priority || 'Low')}</span></td>
										<td>${formattedDate}</td>
									</tr>
								`;
							}).join("")}
						</tbody>
					</table>
				</div>
				<div class="mm-table-footer">
					<span>${__("Showing {0} of {1}", [visibleTasks.length, filteredTasks.length])}</span>
					${hasMoreTasks ? `<button class="btn btn-default mm-show-more">${__("Show More")}</button>` : ""}
				</div>
			`);

			this.$tasksTable.find(".mm-row-link").on("click", (event) => {
				const $row = $(event.currentTarget);
				frappe.set_route("Form", $row.data("doctype"), $row.data("name"));
			});

			this.$tasksTable.find(".mm-show-more").on("click", () => {
				this.recentTaskVisibleCount += this.recentTaskInitialLimit;
				this.render_tables(this.currentData || data, filters || {});
			});
		}

		// Table 2: Recent Events
		const recentEvents = data.events || [];
		if (!recentEvents.length) {
			this.$eventsTable.html(`<div class="mm-empty">${__("No upcoming events found.")}</div>`);
		} else {
			this.$eventsTable.html(`
				<div class="mm-table-wrap">
					<table class="table table-hover">
						<thead>
							<tr>
								<th>${__("Event Subject")}</th>
								<th>${__("Start Time")}</th>
								<th>${__("End Time")}</th>
							</tr>
						</thead>
						<tbody>
							${recentEvents.slice(0, 10).map((e) => {
								const startStr = e.starts_on ? frappe.datetime.str_to_user(e.starts_on) : '-';
								const endStr = e.ends_on ? frappe.datetime.str_to_user(e.ends_on) : '-';
								return `
									<tr class="mm-row-link" data-doctype="Event" data-name="${frappe.utils.escape_html(e.name)}">
										<td><strong>${frappe.utils.escape_html(e.subject || 'Meeting')}</strong></td>
										<td><span class="mm-pill">${startStr}</span></td>
										<td><span class="mm-pill">${endStr}</span></td>
									</tr>
								`;
							}).join("")}
						</tbody>
					</table>
				</div>
			`);

			this.$eventsTable.find(".mm-row-link").on("click", (event) => {
				const $row = $(event.currentTarget);
				frappe.set_route("Form", $row.data("doctype"), $row.data("name"));
			});
		}
	}
}
