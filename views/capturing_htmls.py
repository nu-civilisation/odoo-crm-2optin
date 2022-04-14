# -*- coding: utf-8 -*-
# Developed by nu-civilisation. See LICENSE file for full copyright and licensing details.

from odoo import _
from odoo import http
from ..models.crm_2optin_configs import Crm2optinConfigs
# full python path is: odoo.addons.happiness_profile.models.happiness_profile_testqas


class Crm2optinCapturingHtmls:

    @staticmethod
    def renderCapturingLeadHtml(config, params):
        err = params.get("err")
        content = []
        content.append('<div><table align="center"><form method="POST" action="' + http.request.httprequest.full_path + '">')
        if err:
            if err == "name":
                content.append('<tr><td width="100%">(!)   ' + _('Please proivide a name.') + '</td></tr>')
            if err == "email":
                content.append('<tr><td width="100%">(!)   ' + _('Please provide an e-mail.') + '</td></tr>')
            if err == "state":
                content.append('<tr><td width="100%">(!)   ' + _('Please provide a state for this country.') + '</td></tr>')
        if config.has_postal_address and params.get("country_id"):
            content.append('<tr><td width="100%">(i)   ' + _('Now you can enter the state.') + '</td></tr>')
        content.append('<tr><td width="30%">' + _('Name') + ':</td><td width="70%"><input type="text" id="name" name="name" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_name) + '" value="' + Crm2optinCapturingHtmls._s(params.get('name')) + '" required/></td></tr>')
        content.append('<tr><td width="30%">' + _('E-Mail') + ':</td><td width="70%"><input type="text" id="email" name="email" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_email) + '" value="' + Crm2optinCapturingHtmls._s(params.get('email')) + '" required/></td></tr>')
        if config.has_phone_number:
            content.append('<tr><td width="30%">' + _('Phone Number') + ':</td><td width="70%"><input type="text" id="phone_mumber" name="phone_number" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_phone_number) + '" value="' + Crm2optinCapturingHtmls._s(params.get('phone_number')) + '"/></td></tr>')
        if config.has_postal_address:
            content.append('<tr><td width="30%">' + _('Street Line #1') + ':</td><td width="70%"><input type="text" id="street1" name="street1" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_street1) + '" value="' + Crm2optinCapturingHtmls._s(params.get('street1')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('Street Line #2') + ':</td><td width="70%"><input type="text" id="street2" name="street2" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_street2) + '" value="' + Crm2optinCapturingHtmls._s(params.get('street2')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('ZIP') + ':</td><td width="70%"><input type="text" id="zip" name="zip" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_zip) + '" value="' + Crm2optinCapturingHtmls._s(params.get('zip')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('City') + ':</td><td width="70%"><input type="text" id="city" name="city" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_city) + '" value="' + Crm2optinCapturingHtmls._s(params.get('city')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('State') + ':</td><td width="70%">')
            Crm2optinCapturingHtmls._renderSelectState(content, params.get('country_id'), params.get('state_id'))
            content.append('</td></tr>')
            content.append('<tr><td width="30%">' + _('Country') + ':</td><td width="70%">')
            Crm2optinCapturingHtmls._renderSelectCountry(content, params.get('country_id'))
            content.append('</td></tr>')
        content.append('<tr><td></td><td><input type="submit" name="submit" value="' + Crm2optinCapturingHtmls._s(config.label_submit, 'OK.') + '" class="button-primary"/>')
        content.append('</form></table></div>')

        return ''.join(content)
        # ...important: always return!

    @staticmethod
    def _s(value, default=''):
        if value:
            return str(value)
        elif default:
            return str(default)
        else:
            return ''

    @staticmethod
    def _renderSelectState(content, country_id, default_state_id):
        content.append('<select name="state_id" id="state_id">')
        if country_id:
            countries = http.request.env["res.country"].sudo().search(args=[("id", "=", country_id)])
            for country in countries:
                if country.state_required:
                    content.append('<option value=""> </option>')
            states = http.request.env["res.country.state"].sudo().search(args=[('country_id', '=', country_id)], order='name asc')
            for state in states:
                content.append('<option value="' + str(state.id) + '"')
                if state.id == default_state_id:
                    content.append(' selected')
                content.append('>' + state.name + '</option>')
        else:
            content.append('<option value="">' + _('Please select a country first.') + '</option>')
        content.append('</select>')

        return content

    @staticmethod
    def _renderSelectCountry(content, default_country_id):
        content.append('<select name="country_id" id="country_id">')
        records = http.request.env["res.country"].sudo().search(args=[])
        for record in records:
            content.append('<option value="' + str(record.id) + '"')
            if record.id == default_country_id:
                content.append(' selected')
            content.append('>' + record.name + '</option>')
        content.append('</select>')

        return content
