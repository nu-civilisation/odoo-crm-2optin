# -*- coding: utf-8 -*-
# Developed by nu-civilisation. See LICENSE file for full copyright and licensing details.

import uuid
import urllib.parse
from datetime import datetime
from odoo import fields
from odoo import http
from dateutil.relativedelta import relativedelta
from ..views.capturing_htmls import Crm2optinCapturingHtmls
# full python path is: odoo.addons.crm_2optin.models.happiness_profile_testqas


class CapturingLeadsController(http.Controller):

    @http.route(route="/crm/2optin/form/<uuid:config_uuid>", type="http", auth="public", methods=["GET"], csrf=False, website=True)
    def renderCaptureLead(self, config_uuid, **kwargs):
        # TODO it is a good idea to provide an url check, from where this capture lead is called ... like for vimeo iframes
        configs = http.request.env["crm.2optin.configs"].sudo().search(args=[("uuid", "=", config_uuid)])
        content = ""
        for config in configs:
            htmltext = Crm2optinCapturingHtmls.renderCapturingLeadHtml(config, http.request.params)
            content = str(http.request.render("crm_2optin.crm_2optin_template_capture_lead", lazy=False))
            # ...Deliberately set lazy rendering to false; this ensures, that the string is rendererd immediately.
            content = content.replace("[capture_lead]", htmltext)
            # ...Apply the generated HTML-text in the shortcode "[capture_lead]".

        return content

    @http.route(route="/crm/2optin/form/<uuid:config_uuid>", type="http", auth="public", methods=["POST"], csrf=False, website=True)
    def processCaptureLead(self, config_uuid, **kwargs):
        # in the res.country is a field, that determines, if states are required!
        configs = http.request.env["crm.2optin.configs"].sudo().search(args=[("uuid", "=", config_uuid)])
        for config in configs:
            name = kwargs.get("name")
            email = kwargs.get("email")
            phone_number = kwargs.get("phone_number")
            street1 = kwargs.get("street1")
            street2 = kwargs.get("street2")
            zip = kwargs.get("zip")
            city = kwargs.get("city")
            state_id = kwargs.get("state_id")
            country_id = kwargs.get("country_id")

            err = ""
            if not name:
                err = "name"
            elif not email:
                err = "email"
            elif config.has_postal_address and country_id:
                countries = http.request.env["res.country"].sudo().search(args=[("id", "=", country_id)])
                for country in countries:
                    states = http.request.env["res.country.state"].sudo().search(args=[('country_id', '=', country_id)])
                    for state in states:
                        if state.country_id != country_id:
                            state_id = None
                    if country.state_required and not state_id:
                        err = "state"

            if err:
                # Redirect to the form again to fix the error(s):
                urlquery = []
                urlquery.append("?err=" + urllib.parse.quote(err, safe=""))
                if name:
                    urlquery.append("&name=" + urllib.parse.quote(name, safe=""))
                if email:
                    urlquery.append("&email=" + urllib.parse.quote(email, safe=""))
                if phone_number:
                    urlquery.append("&phone_number=" + urllib.parse.quote(phone_number, safe=""))
                if street1:
                    urlquery.append("&street1=" + urllib.parse.quote(street1, safe=""))
                if street2:
                    urlquery.append("&street2=" + urllib.parse.quote(street2, safe=""))
                if zip:
                    urlquery.append("&zip=" + urllib.parse.quote(zip, safe=""))
                if city:
                    urlquery.append("&city=" + urllib.parse.quote(city, safe=""))
                if state_id:
                    urlquery.append("&state_id=" + state_id)
                if country_id:
                    urlquery.append("&country_id=" + country_id)
                redirectUrl = http.request.httprequest.host_url + "crm/2optin/form/" + str(config.uuid) + ''.join(urlquery)
                return http.request.redirect(redirectUrl)
            else:
                # Store the values in the DB:
                values = {
                    "name": name,
                    "email": email,
                    "config_id": self._int(config.id),
                    "until": fields.Date.today() + relativedelta(days=config.until_days)
                }
                if config.has_phone_number:
                    values["phone_number"] = phone_number
                if config.has_postal_address:
                    values["street1"] = street1
                    values["street2"] = street2
                    values["zip"] = zip
                    values["city"] = city
                    values["state_id"] = self._int(state_id)
                    values["country_id"] = self._int(country_id)
                lead = http.request.env["crm.2optin.leads"].sudo().create([values])

                # Send the token-e-mail:
                email_subject = self._applyPlaceholders(config.email_subject, lead, config)
                email_htmlbody = self._applyPlaceholders(config.email_body, lead, config)
                email_htmlbody = self._applyToken(email_htmlbody, lead)
                values = {
                    "email_from": self._sanitize(config.email_from),
                    # ...Sanitizes the email from field.
                    "email_to": self._sanitize(lead.email),
                    # ...Sanitizes the email to field.
                    "subject": self._sanitize(email_subject),
                    # ...Sanitizes the email subject field.
                    "body_html": email_htmlbody,
                    "auto_delete": str(config.email_autodelete),
                }
                mail_ids = http.request.env["mail.mail"].sudo().create(values)
                for mail_id in mail_ids:
                    mail_id.sudo().send()
                    # ...Sends the e-mail as multipart automatically creating an alternative text message from the HTML message.

                # Redirect to the thank-you page:
                return http.request.redirect(http.request.httprequest.host_url + "crm/2optin/token/" + str(config_uuid))
        return http.request.render('website.404')
        # ...When the config UUID wasn't found, then redirect to HTTP 404.

    @http.route(route="/crm/2optin/token/<uuid:config_uuid>", type="http", auth="public", methods=["GET"], csrf=False, website=True)
    def renderEnterToken(self, config_uuid, **kwargs):
        # TODO it is a good idea to provide an url check, from where this senter token is called ... like for vimeo iframes
        content = ""
        configs = http.request.env["crm.2optin.configs"].sudo().search(args=[("uuid", "=", config_uuid)])
        for config in configs:
            htmltext = Crm2optinCapturingHtmls.renderEnterTokenHtml(config, http.request.params)
            content = str(http.request.render("crm_2optin.crm_2optin_template_enter_token", lazy=False))
            # ...Deliberately set lazy rendering to false; this ensures, that the string is rendererd immediately.
            content = content.replace("[enter_token]", htmltext)
            # ...Apply the generated HTML-text in the shortcode "[enter_token]".

        return content

    @http.route(route="/crm/2optin/token/<uuid:config_uuid>", type="http", auth="public", methods=["POST"], csrf=False, website=True)
    def processEnterToken(self, config_uuid, **kwargs):
        configs = http.request.env["crm.2optin.configs"].sudo().search(args=[("uuid", "=", config_uuid)])
        for config in configs:
            token = kwargs.get("token")
            lead_ids = http.request.env["crm.2optin.leads"].sudo().search(args=[("token_uuid", "=", token)])
            for lead_id in lead_ids:
                return http.request.redirect(http.request.httprequest.host_url + "crm/2optin/confirm/" + str(token))
                # ...Redirect to the confirmation page.
            redirectUrl = http.request.httprequest.host_url + "crm/2optin/token/" + str(config.uuid) + '?err=' + token
            return http.request.redirect(redirectUrl)
            # ...Redirect to the current page.
        return http.request.render('website.404')
        # ...When the config UUID wasn't found, then redirect to HTTP 404.

    @http.route(route="/crm/2optin/confirm/<uuid:token_uuid>", type="http", auth="public", methods=["GET"], csrf=False, website=True)
    def renderConfirmation(self, token_uuid, **kwargs):
        # TODO it is a good idea to provide an url check, from where this capture lead is called ... like for vimeo iframes
        lead_ids = http.request.env["crm.2optin.leads"].sudo().search(args=[("token_uuid", "=", token_uuid)])
        for lead_id in lead_ids:
            values = {
                "name": lead_id.name,
                "email": lead_id.email,
            }
            if lead_id.phone_number:
                values["phone"] = lead_id.phone_number
            if lead_id.street1:
                values["street"] = lead_id.street1
            if lead_id.street2:
                values["street2"] = lead_id.street2
            if lead_id.zip:
                values["zip"] = lead_id.zip
            if lead_id.city:
                values["city"] = lead_id.city
            if lead_id.state_id:
                values["state_id"] = lead_id.state_id.id
            if lead_id.country_id:
                values["country_id"] = int(lead_id.country_id.id)
            http.request.env["res.partner"].sudo().create([values])
            # ...Create the new partner as contact.

            lead_id.sudo().unlink()
            # ...The lead has done it's task -- now delete it, since it is not used any more.

            today = datetime.now().date()
            today_str = datetime.strftime(today, "%Y-%m-%d 00:00:00")
            lead_ids = http.request.env["crm.2optin.leads"].sudo().search([("until", "<", today_str)])
            for lead_id in lead_ids:
                lead_id.sudo().unlink()
                # ...For sanity, delete all leads, which have passed the current day.

            return "Confirmation!"
        return "No token UUID found."

    def _applyPlaceholders(self, content, lead, config):
        content = content.replace("[name]", lead.name)
        content = content.replace("[email]", lead.email)
        content = content.replace("[until]", lead.until.strftime("%Y-%m-%d"))
        if config.has_phone_number and lead.phone_number:
            if lead.phone_number:
                content = content.replace("[phone_number]", lead.phone_number)
            else:
                content = content.replace("[phone_number]", "")
        if config.has_postal_address:
            if lead.street1:
                content = content.replace("[street1]", lead.street1)
            else:
                content = content.replace("[street1]", "")
            if lead.street2:
                content = content.replace("[street2]", lead.street2)
            else:
                content = content.replace("[street2]", "")
            if lead.zip:
                content = content.replace("[zip]", lead.zip)
            else:
                content = content.replace("[zip]", "")
            if lead.city:
                content = content.replace("[city]", lead.city)
            else:
                content = content.replace("[city]", "")
            if lead.state_id:
                content = content.replace("[state]", lead.state_id.name)
            else:
                content = content.replace("[state]", "")
            if lead.country_id:
                content = content.replace("[country]", lead.country_id.name)
            else:
                content = content.replace("[country]", "")
        return content

    def _applyToken(self, content, lead):
        if lead.token_uuid:
            content = content.replace("[token]", lead.token_uuid)
            content = content.replace("[token_link]", http.request.httprequest.host_url + "crm/2optin/confirm/" + lead.token_uuid)
        return content

    def _sanitize(self, string):
        if string:
            for crlf in ["\n", "\r"]:
                string = string.replace(crlf, "")
            return string
        else:
            return ""

    def _int(self, value):
        if value:
            return int(value)
        else:
            return None
