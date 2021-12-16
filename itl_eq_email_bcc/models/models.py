# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.eq_email_bcc.models.mail import mail_template


def generate_email(self, res_ids, fields=None):
    self.ensure_one()
    return super(mail_template, self).generate_email(res_ids, fields)


# NOTE: Basically we are changing the method on eq_email_bcc due is not working
mail_template.generate_email = generate_email


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    def generate_email(self, res_ids, fields=None):
        self.ensure_one()
        # TODO (jovani.martinez): This is not the best practice due if Odoo changes
        #  something related to this fields this must fail, but the way Odoo is build
        #  and the way eq_email_bcc is not taking in count email_bcc as jinja object.
        fields = [
            'subject', 'body_html', 'email_from', 'email_to', 'partner_to',
            'email_cc', 'reply_to', 'scheduled_date', 'email_bcc']
        return super(MailTemplate, self).generate_email(res_ids, fields)
