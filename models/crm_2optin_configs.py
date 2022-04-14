# -*- coding: utf-8 -*-
# Developed by nu-civilisation. See LICENSE file for full copyright and licensing details.

import uuid
from odoo import _
from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import ValidationError


class Crm2optinConfigs(models.Model):
    _name = "crm.2optin.configs"
    _description = "CRM Double-OptIn-Configurations"

    uuid = fields.Char(string="UUID", required=True, index=True, readonly=True, default=lambda self: str(uuid.uuid4()))
    name = fields.Char(string="Name", translate=True, required=True)
    has_phone_number = fields.Boolean(string="Capture Phone-Number?", default=False)
    has_postal_address = fields.Boolean(string="Capture Postal Address?", default=False)
    smtp_server_ids = fields.Many2one(comodel_name="ir.mail_server", string="Outgoing Mail Server", required=True)
    email_from = fields.Char(string="E-Mail From", required=True)
    email_subject = fields.Char(string="E-Mail Subject", required=True)
    email_body = fields.Html(string="E-Mail Body", required=True, sanitize=False, sanitize_tags=False, sanitize_attributes=False, sanitize_style=False, strip_style=False, strip_classes=False)
    email_autodelete = fields.Boolean(string="Email Autodelete?", required=True)
    until_days = fields.Integer(string="Days until leads must be confirmed", required=True, default=3)
    placeholder_name = fields.Char(string="Placeholder Name", translate=True)
    placeholder_email = fields.Char(string="Placeholder E-Mail", translate=True)
    placeholder_phone_number = fields.Char(string="Placeholder Phone Number", translate=True)
    placeholder_street1 = fields.Char(string="Placeholder Street Line #1", translate=True)
    placeholder_street2 = fields.Char(string="Placeholder Street Line #2", translate=True)
    placeholder_zip = fields.Char(string="Placeholder ZIP", translate=True)
    placeholder_city = fields.Char(string="Placeholder City", translate=True)
    label_submit = fields.Char(string="Label Submit", translate=True)

    @api.constrains("until_days")
    def _check_until_days(self):
        for record in self:
            if record.until_days < 1 or record.until_days > 365:
                raise ValidationError(_("Until-days must be positive ant no more than 365 days, but are: " + str(record.until_days)))
