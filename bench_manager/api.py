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
from subprocess import check_output, Popen, PIPE
from bench_manager.utils import verify_whitelisted_call, safe_decode
from bench_manager.doctype.site.site import pass_exists
from frappe.utils.data import get_datetime, now_datetime
import os, re, json, time, pymysql, shlex
from subprocess import Popen, PIPE, STDOUT
import re, shlex


@frappe.whitelist(allow_guest=True)
def verify_account(name, code):
	site = frappe.get_doc("Site Request", name)
	if site.status != "Email Sent":
		return "The site does not need verification"
	if site.email_verification_code == code:
		#~ frappe.db.sql("""update `tabSite Request` set `status`="Site Verified"
				#~ where namet=%s""", doctype)
		site.flags.ignore_permissions = True
		site.status = "Site Verified"
		site.save(ignore_permissions=1)
		frappe.db.commit()
		main_domain = frappe.db.get_value("SAAS Settings", None, "main_domain")
		mysql_password = frappe.db.get_value("SAAS Settings", None, "mysql_password")
		#~ create_site(site.subdomain + "nasaqerp.com" , "true" , "123" ,"123",now_datetime())
		create_site(site_name=site.subdomain + "."+main_domain , install_erpnext="true" ,
			mysql_password= "newpwd" ,admin_password="123",key=site.subdomain +"."+main_domain +str(now_datetime()) ,email = site.email)

		return "https://nama.tech"
	else:
		return "Wapi"



@frappe.whitelist()
def create_site(site_name, install_erpnext, mysql_password, admin_password, key):
	verify_whitelisted_call()
	commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=site_name,
		admin_password=admin_password, mysql_password=mysql_password)]
	if install_erpnext == "true":
		with open('apps.txt', 'r') as f:
			app_list = f.read()
		if 'erpnext' not in app_list:
			commands.append("bench get-app erpnext")
		commands.append("bench --site {site_name} install-app erpnext".format(site_name=site_name))
		if 'charity' in app_list:
			commands.append("bench --site {site_name} install-app charity".format(site_name=site_name))
	frappe.enqueue('bench_manager.bench_manager.utils.run_command',
		commands=commands,
		doctype="Bench Settings",
		key=key
	)
	all_sites = safe_decode(check_output("ls")).strip('\n').split('\n')
	while site_name not in all_sites:
		time.sleep(2)
		print("waiting for site creation...")
		all_sites = safe_decode(check_output("ls")).strip('\n').split('\n')
	doc = frappe.get_doc({'doctype': 'Site', 'site_name': site_name, 'app_list':'frappe', 'developer_flag':1})
	doc.insert()
	frappe.db.commit()
