// Copyright (c) 2020, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('SaaS Send Invoice', {
	send_email: function(frm) {
		if(cur_frm.doc.sales_invoice){

			frappe.confirm(
			    'Are you sure you want to send an email?',
			    function(){

			    	frappe.call({
			            method: "send_invoice_email",
			            doc: cur_frm.doc,
			            callback: function(r) {
			            	show_alert('Email sent successfully!')
			            }
			        });
			    	
			    },
			    function(){
			        window.close();
			    }
			)

		}
	}
});
