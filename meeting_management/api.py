from frappe import _

# Customer Dashboard
def customer_get_data():
	return {
		"heatmap": True,
		"heatmap_message": _(
			"This is based on transactions against this Customer. See timeline below for details"
		),
		"fieldname": "customer",
		"non_standard_fieldnames": {
			"Payment Entry": "party",
			"Quotation": "party_name",
			"Opportunity": "party_name",
			"Bank Account": "party",
			"Subscription": "party",
            'Meeting':'party',
            "Meeting Schedule":'party'
		},
		"dynamic_links": {"party_name": ["Customer", "quotation_to"]},
		"transactions": [
			{"label": _("Pre Sales"), "items": ["Opportunity", "Quotation"]},
			{"label": _("Orders"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
			{"label": _("Payments"), "items": ["Payment Entry", "Bank Account"]},
			{
				"label": _("Support"),
				"items": ["Issue", "Maintenance Visit", "Installation Note", "Warranty Claim"],
			},
			{"label": _("Projects"), "items": ["Project"]},
			{"label": _("Pricing"), "items": ["Pricing Rule"]},
			{"label": _("Subscriptions"), "items": ["Subscription"]},
            {"label": _("Meeting"), "items": ["Meeting" ,'Meeting Schedule']},
		],
	}

# Lead Dashboard
def lead_get_data(data):
	return {
		'fieldname': 'lead',
		'non_standard_fieldnames': {
			'Quotation': 'party_name',
			'Opportunity': 'party_name',
			"Meeting": "party",
			"Meeting Schedule": "party",
		},
		'dynamic_links': {
			'party_name': ['Lead', 'quotation_to'],
		},
		'transactions': [
			{
				'items': ['Opportunity', 'Quotation','Meeting Schedule','Meeting']
			},
		]
	}

