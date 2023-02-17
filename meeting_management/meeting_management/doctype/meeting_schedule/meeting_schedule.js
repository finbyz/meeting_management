this.frm.add_fetch('contact', 'email_id', 'email_id');

cur_frm.set_query("contact", function() {
	return {
		query: "frappe.contacts.doctype.contact.contact.contact_query",
		filters: { link_doctype: cur_frm.doc.party_type, link_name: cur_frm.doc.party } 
	};
});

frappe.ui.form.on('Meeting Schedule', {
	refresh: function(frm) {
		frm.add_custom_button(__("Create Meeting"), function() {
			frappe.model.open_mapped_doc({
				method : "meeting_management.meeting_management.doctype.meeting_schedule.meeting_schedule.make_meeting",
				frm : frm
			})
		})
	
	},

	email_template:function(frm){
		frm.call({
			method:"frappe.email.doctype.email_template.email_template.get_email_template",
			args:{
				template_name:frm.doc.email_template,
				doc:frm.doc
			},
			callback: function(r){
				
				frm.set_value("invitation_message", r.message.message)

			}
		})
	},

	
	scheduled_from(frm) {
		if (frm.doc.scheduled_from && !frm.doc.scheduled_to){
		    // frm.set_value('scheduled_to',frm.doc.scheduled_from)
			frm.set_value('scheduled_to',frappe.datetime.get_datetime_as_string(frappe.datetime.str_to_obj(frm.doc.scheduled_from).setHours(frappe.datetime.str_to_obj(frm.doc.scheduled_from).getHours() + 1)))
		}
	},
	validate: function(frm){
		frm.trigger("set_link_documents");
		// frm.trigger("contact_person_name")
	},

	contact_person_name: function(frm) {
		if(frm.doc.contact || frm.doc.contact_person_name){
			let datetime = frappe.datetime.global_date_format(frm.doc.scheduled_from).split(", ");
			let date = datetime[0] || '';
			let time = datetime[1]+"." || '';
			let sign = frappe.boot.user.email_signature || '';
			let is_online = "";
			if(frm.doc.is_online){
				is_online = " Online ";
			}
			let message = "<p>Dear " + frm.doc.contact_person_name + ",</p><p>Greeting from "+ frm.doc.company + "</p><p> This is regarding the telephonic conversation that we had" + ". The" + is_online + " Meeting has been scheduled on " + date + " at " + time + "</p><p>In case of Any Changes in your Schedule request you to inform us timely.</p><p></p>Thanks & Regards,<p>" + sign + "</p>";
			frm.set_value("invitation_message", message);
		}
	},

	party_type: function(frm){
		frm.set_value('party','');
		frm.set_value('contact', '');
		frm.set_value('organisation', '');
		frm.set_value('contact_person_name', '');
		frm.set_value('mobile_no', '');
		frm.set_value('email_id', '');
		frm.set_value('invitation_message', '');
	},
	party: function(frm) {
		if(frm.doc.party){
			frm.trigger("get_party_details");
			frm.trigger("set_link_documents");
		}
	},
	set_link_documents: function(frm){
		if(frm.doc.party){
			if(frm.doc.party_type=="Lead"){
				frm.set_value("lead",frm.doc.party)
			}
			else if(frm.doc.party_type=="Customer"){
				frm.set_value("customer",frm.doc.party)
			}
			else if(frm.doc.party_type=="Opportunity"){
				frm.set_value("opportunity",frm.doc.party)
			}
		}		
	},
	get_party_details: function(frm){
		frappe.call({
			method:"meeting_management.meeting_management.doctype.meeting_schedule.meeting_schedule.get_party_details",
			args:{
				party: frm.doc.party,
				party_type: frm.doc.party_type
			},
			callback: function(r){
				if(r.message){
					frm.set_value('contact', r.message.contact_person);
					frm.set_value('contact_person_name', r.message.contact_display);
					frm.set_value('mobile_no', r.message.contact_mobile);
					frm.set_value('email_id', r.message.contact_email);
					frm.set_value('organisation', r.message.organisation);
				}
			}
		})
	},
	send_invitation: function(frm){
		if (frm.is_dirty()){
			frappe.throw("Please Save the Current Document and Then Proceed again")
		}
		else{
			frm.call('send_invitation');
		}
	}
});