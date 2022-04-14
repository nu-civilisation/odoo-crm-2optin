# -*- coding: utf-8 -*-
# Developed by nu-civilisation. See LICENSE file for full copyright and licensing details.

import uuid
from odoo import api
from odoo import fields
from odoo import models
from dateutil.relativedelta import relativedelta


class Crm2optinLeads(models.Model):
    _name = "crm.2optin.leads"
    _description = "CRM Double-OptIn-Leads"

    name = fields.Char(string="Name", translate=True, required=True, index=True)
    email = fields.Char(string="E-Mail-Address", required=True, index=True)
    config_id = fields.Many2one(comodel_name="crm.2optin.configs", string="Configuration", required=True)
    token_uuid = fields.Char(string="Token-UUID", required=True, index=True, readonly=True, default=lambda self: str(uuid.uuid4()))
    # ...Deliberately use UUID v4 to guarantee randomness.
    until = fields.Date(string="Confirm until?", required=True, readonly=True, copy=False)
    capture_phone_number = fields.Boolean(compute="_compute_capturePhoneNumber")
    capture_postal_address = fields.Boolean(compute="_compute_capturePostalAddress")
    # postal_address = fields.Char(string="Postal Address", compute="_compute_postalAddress", readonly=True)
    phone_number = fields.Char(string="Phone Number")
    street1 = fields.Char(string="Street Line #1")
    street2 = fields.Char(string="Street Line #2")
    zip = fields.Char(string="ZIP")
    city = fields.Char(string="City")
    state_id = fields.Many2one(comodel_name="res.country.state", string="State", ondelete="restrict", domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one(comodel_name="res.country", string="Country", ondelete="restrict")

    @api.depends("config_id.has_phone_number")
    def _compute_capturePhoneNumber(self):
        for record in self:
            record.capture_phone_number = record.config_id.has_phone_number

    @api.depends("config_id.has_postal_address")
    def _compute_capturePostalAddress(self):
        for record in self:
            record.capture_postal_address = record.config_id.has_postal_address

    # @api.depends("capture_postal_address", "street1", "street2", "zip", "city", "state_id.name", "country_id.name")
    def _compute_postalAddress(self):
        for record in self:
            _postalAddress = "Hi there!"
            if record.capture_postal_address:
                pass
                # if record.street1 and record.street1.strip():
                #     _postalAddress += record.street.strip()
                # if record.street2 and record.street2.strip():
                #     _postalAddress += ", " + record.street2.strip()
                # if record.zip and record.zip.strip():
                #     _postalAddress += ", " + record.zip.strip()
                # if record.city and record.city.strip():
                #     _postalAddress += " " + record.city.strip()
                # if record.state_id and record.state_id.name:
                #     _postalAddress += ", " + record.state_id.name
                # if record.country_id and record.country_id.name:
                #     _postalAddress += ", " + record.country_id.name

            return _postalAddress

    def _get_country_name(self):
        return self.country_id.name or ''

    @api.onchange('state_id')
    def _onchange_state(self):
        for record in self:
            if record.state_id.country_id:
                record.country_id = record.state_id.country_id

    @api.onchange('country_id')
    def _onchange_country_id(self):
        for record in self:
            if record.country_id and record.country_id != record.state_id.country_id:
                record.state_id = False
