frappe.pages['meeting-calender'].on_page_load = function(wrapper) {

	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Meeting Calendar',
		single_column: true
	});

	// Main page full width
	$('.layout-side-section').hide();

	$('.layout-main-section-wrapper').css({
		width: '100%',
		maxWidth: '100%',
		paddingLeft: '0'
	});

	// Remove padding
	$('.layout-main').css({
		padding: '0'
	});

	// Iframe
	const iframe = $(`
		<iframe
			src="/app/event/view/calendar"
			style="
				width:100%;
				height:100vh;
				border:none;
				background:#fff;
			"
		></iframe>
	`);

	$(page.main).append(iframe);

	// After iframe load
	iframe.on('load', function() {

		const iframe_doc = this.contentWindow.document;

		// Inject styles
		const style = iframe_doc.createElement('style');

		style.innerHTML = `
			.navbar,
			.page-head,
			.layout-side-section,
			.layout-side-section-wrapper,
			.standard-sidebar,
			.desk-sidebar,
			.list-sidebar {
				display: none !important;
				width: 0 !important;
				min-width: 0 !important;
			}
			.body-sidebar{
				visibility: hidden !important;}
			.layout-main-section-wrapper,
			.layout-main-section {
				width: 100% !important;
				max-width: 100% !important;
				padding-left: 0 !important;
				margin-left: 0 !important;
			}

			.layout-main {
				padding: 0 !important;
			}

			body {
				margin: 0 !important;
				overflow: hidden !important;
			}
		`;

		iframe_doc.head.appendChild(style);

		// Repeatedly remove sidebar
		setInterval(() => {

			$(iframe_doc).find(`
				.layout-side-section,
				.layout-side-section-wrapper,
				.standard-sidebar,
				.desk-sidebar,
				.list-sidebar
			`).remove();

			$(iframe_doc).find('.layout-main-section-wrapper').css({
				width: '100%',
				maxWidth: '100%',
				paddingLeft: '0',
				marginLeft: '0'
			});

		}, 500);
	});
};

// Restore sidebar when leaving page
frappe.pages['meeting-calender'].on_page_leave = function() {

	$('.layout-side-section').show();

	$('.layout-main-section-wrapper').css({
		width: '',
		maxWidth: '',
		paddingLeft: ''
	});
};