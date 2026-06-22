// frappe.pages['meeting-links'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Personal Meeting Links',
// 		single_column: true
// 	});
// }

frappe.pages['meeting-links'].on_page_load = async function(wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Personal Meeting Links',
		single_column: true
	});

	const container = $(`
		<div style="padding:20px;">
			<div class="table-responsive">
				<table class="table table-bordered">
					<thead>
						<tr>
							<th>User</th>
							<th>Personal Meeting Link</th>
						</tr>
					</thead>

					<tbody id="meeting-links-body">
						<tr>
							<td colspan="2" class="text-center">
								Loading...
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	`).appendTo(page.main);

	const tbody = $("#meeting-links-body");

	try {

		const r = await frappe.call({
			method: "meeting_management.meeting_management.page.meeting_links.meeting_links.get_meeting_links"
		});

		let data = r.message || [];

		if (!data.length) {

			tbody.html(`
				<tr>
					<td colspan="2" class="text-center text-muted">
						No Records Found
					</td>
				</tr>
			`);

			return;
		}

		let rows = "";

		data.forEach(row => {

			rows += `
				<tr>
					<td>
						${row.full_name || row.user}
					</td>

					<td style="word-break: break-all;">
						${row.personal_meeting_link}
					</td>
				</tr>
			`;
		});

		tbody.html(rows);

	} catch (e) {

		console.error(e);

		tbody.html(`
			<tr>
				<td colspan="2" class="text-danger text-center">
					Error loading data
				</td>
			</tr>
		`);
	}
};