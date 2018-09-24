// Copyright (c) 2018, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Request', {
	refresh: function(frm) {

	},
	send_confirmation_email: function(frm) {
		if (frm.doc.status==="Pending Approval"){
			frappe.call({
				method: "bench_manager.bench_manager.doctype.site_request.site_request.notify_user",
				args: {
					doc: frm.doc.name
				},
				callback: function(r){
					
				}
			})
		}
	}
});
