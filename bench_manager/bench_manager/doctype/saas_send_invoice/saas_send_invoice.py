# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, nowdate, cint
import datetime
from frappe import utils
from datetime import date
from frappe.utils.data import flt, nowdate, getdate, cint
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate , add_days, get_url
from frappe.model.document import Document


class SaaSSendInvoice(Document):
    @frappe.whitelist(allow_guest=True)
    def send_invoice_email(self):
        f = open("/home/erp/frappe-bench/apps/bench_manager/bench_manager/templates/emails/saas_send_invoice.html", "w")
        f.write(self.email_template)
        f.close()

        doc = frappe.get_doc("Sales Invoice", self.sales_invoice)
        msg = frappe.render_template('bench_manager/templates/emails/saas_send_invoice.html', context={"customer": doc.customer, "name": doc.name, "grand_total": doc.grand_total, "items": doc.items})
        sender = frappe.get_value("Email Account", filters = {"default_outgoing": 1}, fieldname = "email_id") or None
        recipient = frappe.get_value("Customer", {"name": doc.customer}, "customer_email")

        frappe.sendmail(sender=sender, recipients= recipient,
            content=msg, subject="Sales Invoice", delayed=True)

        return 'Email Sent'




