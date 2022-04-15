# -*- coding: utf-8 -*-
# Developed by nu-civilisation. See LICENSE file for full copyright and licensing details.

import urllib.parse
from odoo import _
from odoo import http
from ..models.crm_2optin_configs import Crm2optinConfigs
# full python path is: odoo.addons.happiness_profile.models.happiness_profile_testqas


class Crm2optinCapturingHtmls:

    @staticmethod
    def renderCapturingLeadHtml(config, params):
        url = http.request.httprequest.host_url + "crm/2optin/form/" + str(config.uuid)
        content = []
        content.append('<div><table align="center"><form method="POST" action="' + url + '">')
        # if err:
        err = params.get("err")
        if err == "name":
            content.append('<tr><td colspan="2">(!)   ' + _('Please proivide a name.') + '</td></tr>')
        elif err == "email":
            content.append('<tr><td colspan="2">(!)   ' + _('Please provide an e-mail.') + '</td></tr>')
        elif err == "state":
            content.append('<tr><td colspan="2">(!)   ' + _('Please provide a state for this country.') + '</td></tr>')
        content.append('<tr><td width="30%">' + _('Name') + ':</td><td width="70%"><input type="text" id="name" name="name" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_name) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('name')) + '"/></td></tr>')
        content.append('<tr><td width="30%">' + _('E-Mail') + ':</td><td width="70%"><input type="text" id="email" name="email" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_email) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('email')) + '"/></td></tr>')
        if config.has_phone_number:
            content.append('<tr><td width="30%">' + _('Phone Number') + ':</td><td width="70%"><input type="text" id="phone_mumber" name="phone_number" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_phone_number) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('phone_number')) + '"/></td></tr>')
        if config.has_postal_address:
            content.append('<tr><td width="30%">' + _('Street Line #1') + ':</td><td width="70%"><input type="text" id="street1" name="street1" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_street1) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('street1')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('Street Line #2') + ':</td><td width="70%"><input type="text" id="street2" name="street2" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_street2) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('street2')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('ZIP') + ':</td><td width="70%"><input type="text" id="zip" name="zip" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_zip) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('zip')) + '"/></td></tr>')
            content.append('<tr><td width="30%">' + _('City') + ':</td><td width="70%"><input type="text" id="city" name="city" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_city) + '" value="' + Crm2optinCapturingHtmls._url_decode(params.get('city')) + '"/></td></tr>')
            country_id = params.get('country_id')
            if country_id and http.request.env["res.country.state"].sudo().search_count(args=[('country_id', '=', int(country_id))]) > 0:
                content.append('<tr><td width="30%">' + _('State') + ':</td><td width="70%">')
                Crm2optinCapturingHtmls._renderSelectState(content, params.get('country_id'), params.get('state_id'))
                content.append('</td></tr>')
            content.append('<tr><td width="30%">' + _('Country') + ':</td><td width="70%">')
            Crm2optinCapturingHtmls._renderSelectCountry(content, params.get('country_id'))
            content.append('</td></tr>')
        content.append('<tr><td></td><td><input type="submit" name="submit" value="' + Crm2optinCapturingHtmls._s(config.label_submit_capture, 'OK.') + '" class="button-primary"/></td></tr>')
        content.append('</form></table></div>')

        return ''.join(content)
        # ...important: always return!

    @staticmethod
    def renderEnterTokenHtml(config, params):
        url = http.request.httprequest.host_url + "crm/2optin/token/" + str(config.uuid)
        content = []
        content.append('<div><table align="center"><form method="POST" action="' + url + '">')
        err = params.get("err")
        if err:
            content.append('<tr><td width="100%">(!)   ' + _('Please proivide a valid token.') + '</td></tr>')
        content.append('<tr><td width="100%"><input type="text" id="token" name="token" placeholder="' + Crm2optinCapturingHtmls._s(config.placeholder_token) + '"/></td></tr>')
        content.append('<tr><td width="100%"><input type="submit" id="submit" name="submit" value="' + Crm2optinCapturingHtmls._s(config.label_submit_token, 'OK.') + '" class="button-primary"/></td></tr>')
        content.append('</form></table></div>')

        return ''.join(content)
        # ...important: always return!

    @staticmethod
    def _renderSelectState(content, country_id, default_state_id):
        content.append('<select name="state_id" id="state_id">')
        if country_id:
            states = http.request.env["res.country.state"].sudo().search(args=[('country_id', '=', int(country_id))], order='name asc')
            for state in states:
                content.append('<option value="' + str(state.id) + '"')
                if str(state.id) == default_state_id:
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
            if str(record.id) == default_country_id:
                content.append(' selected')
            content.append('>' + record.name + '</option>')
        content.append('</select>')

        return content

    @staticmethod
    def _url_decode(value, default=''):
        if value:
            return urllib.parse.unquote(value)
        elif default:
            return str(default)
        else:
            return ''

    @staticmethod
    def _s(value, default=''):
        if value:
            return str(value)
        elif default:
            return str(default)
        else:
            return ''
