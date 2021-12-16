from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback.purchase'
    _description = "Send Message Feedback Purchase"
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        approval_request_id.action_refuse_confirm()
        
        if 'purchase_id' in context:
            purchase_id = self.env['purchase.order'].sudo().browse(context['purchase_id'])
            if purchase_id:
                purchase_id.message_post(body=self.name, subject="Approval request refused")
                purchase_id.button_refused()
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
