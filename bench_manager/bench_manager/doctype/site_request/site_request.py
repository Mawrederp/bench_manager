# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
import string
import random
from frappe.utils.background_jobs import enqueue
import subprocess
import re



class SiteRequest(Document):
	def validate(self):
		self.validate_subdomain()
		
	def after_command(self, commands=None):
		settings = frappe.get_single('SAAS Settings')
		site_name = customer.site_name +"."+settings.main_domain
		mysql_password = settings.mysql_password
		admin_password = settings.admin_password
		email_args = {
			"recipients": doc.email,
			"sender": None,
			"subject": "Your New site created "+site_name,
			"message": "site :"+site_name +"<br>"+ "user :"+"administrator"+"<br>"+"passwored :"+admin_password,
			"now": True,
		}
		enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
		
		
	def validate_subdomain(self):
		if self.subdomain and self.status == "Pending Approval":
			clean_string = ''.join(e for e in self.subdomain if e.isalnum())
			self.subdomain = clean_string.lower()
			frappe.msgprint(_(self.subdomain))


def id_generator(size=50, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.SystemRandom().choice(chars) for _ in range(size))
	
@frappe.whitelist(allow_guest=True)
def notify_user(doc):
	site = frappe.get_doc("Site Request", doc)
	site.check_permission("email")
	main_domain = frappe.db.get_value("SAAS Settings", None, "main_domain")
	
	if site.status == "Pending Approval":
		site.email_verification_code = id_generator()
		frappe.sendmail(
			recipients = [site.email],
			subject="Validate your account",
			message = "Please validate your email, click on this link: https://"+main_domain+"/api/method/bench_manager.api.verify_account?name=%s&code=%s" % (site.name,site.email_verification_code),
			reference_doctype=site.doctype,
			reference_name=site.name
		)
		site.status = "Email Sent"
		site.save()
		frappe.msgprint(_("Confirmation emails sent"))
	else:
		frappe.msgprint(_("Site Status must be 'Pending Approval'"))
		
	return "Finish"
		


@frappe.whitelist(allow_guest=True)
def verify_account(name, code):
	site = frappe.get_doc("Site Request", name)
	if site.status != "Email Sent":
		return "The site does not need verification"
	if site.email_verification_code == code:
		site.status = "Site Verified"
		site.flags.ignore_permissions = True
		site.save()
		enqueue(create_site, site=site.name)
	else:
		return "Wapi"

def create_site_request_and_site(doc, method):
	if doc.user_type == "Website User" and doc.get_db_value("enabled") == 0 and doc.enabled ==1:
		sr_doc = create_site_request(doc, method)

	
def create_site_request(doc, method):
	if doc.user_type == "Website User" and doc.get_db_value("enabled") == 0 and doc.enabled ==1:
		customers = frappe.db.get_list("Customer",{"customer_email":doc.email}, ignore_permissions=True)
		if customers : 
			customer =frappe.get_doc("Customer",{"customer_email":doc.email})
			sits_list = frappe.db.get_list("Site Request",{"email":doc.email})
			if not sits_list:
				sr = frappe.new_doc("Site Request")
				sr.update(dict(
					full_name= doc.full_name,
					email= doc.email,
					employee_count= 0,
					association_name= customer.company_name,
					subdomain= customer.site_name,
					)
				)
				sr.save(ignore_permissions=True)
				from bench_manager.bench_manager.doctype.site.site import create_site_internal
				create_site_internal(doc)
