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


class SiteRequest(Document):
	pass


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

def create_site_request(doc, method):
	
	sr = frappe.new_doc("Site Request")
	sr.update(dict(
		full_name= doc.full_name,
		email= doc.email,
		mobile_number= doc.mobile_number,
		employee_count= doc.employee_count if doc.employee_count else 0,
		association_name= doc.association_name,
		activity= doc.activity if doc.activity else ""
		)
	)
	sr.save(ignore_permissions=True)
