// Copyright (c) 2018, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Request', {
	refresh: function(frm) {

	},
	create_site: function(frm) {
		frappe.model.get_value('SAAS Settings', {'name': 'SAAS Settings'}, 'main_domain',
		  function(d) {
			console.log(d)
			
			frappe.call({
				method: 'bench_manager.bench_manager.doctype.site.site.pass_exists',
				args: {
					doctype: frm.doctype
				},
				btn: this,
				callback: function(r){
					var dialog = new frappe.ui.Dialog({
						fields: [
							{fieldname: 'site_name', fieldtype: 'Data', label: "Site Name", reqd: true,read_only:true,'default':frm.doc.subdomain +"."+d.main_domain},
							{fieldname: 'install_erpnext', fieldtype: 'Check', label: "Install ERPNext",read_only:true,'default':1},
							{fieldname: 'admin_password', fieldtype: 'Password',
								label: 'Administrator Password',
								read_only:true,
								default: d.admin_password
							},
							{fieldname: 'mysql_password', fieldtype: 'Password',
								label: 'MySQL Password',
								default:d.mysql_password ,read_only:true }
						],
					});
					dialog.set_primary_action(__("Create"), () => {
						let key = dialog.fields_dict.site_name.value + frappe.datetime.get_datetime_as_string();
						let install_erpnext;
						if (dialog.fields_dict.install_erpnext.last_value != 1){
							install_erpnext = "false";
						} else {
							install_erpnext = "true";
						}
						frappe.call({
							method: 'bench_manager.bench_manager.doctype.site.site.verify_password',
							args: {
								site_name: dialog.fields_dict.site_name.value,
								mysql_password: dialog.fields_dict.mysql_password.value
							},
							callback: function(r){
								if (r.message == "console"){
									console_dialog(key);
									frappe.call({
										method: 'bench_manager.bench_manager.doctype.site.site.create_site',
										args: {
											site_name: dialog.fields_dict.site_name.value,
											email: frm.doc.email,
											admin_password: dialog.fields_dict.admin_password.value,
											mysql_password: dialog.fields_dict.mysql_password.value,
											install_erpnext: install_erpnext,
											key: key,
											doc:frm.doc
										}
									});
									dialog.hide();
								} 
							}
						});
					});
					dialog.show();
				}
			});
		
			
			
			
			
			
		  })
	
	
	

					
		
		
		
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
