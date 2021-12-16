from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback.partner'
    _description = "Send Message Feedback Partner"
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        approval_request_id.action_refuse_confirm()
        
        if 'partner_id' in context:
            partner_id = self.env['res.partner'].sudo().browse(context['partner_id'])
            if partner_id:
                partner_id.message_post(body=self.name, subject="Approval request refused")
                partner_id.state = 'rejected'
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
