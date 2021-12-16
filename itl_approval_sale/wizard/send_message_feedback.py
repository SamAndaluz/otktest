from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback'
    _description = "Send Message Feedback Sale"
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        _logger.info("--####> sale send_message")
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        _logger.info("####===> approval_request_id: " + str(approval_request_id))
        approval_request_id.action_refuse_confirm(context)
        
        if 'sale_id' in context:
            sale_id = self.env['sale.order'].browse(context['sale_id'])
            if sale_id:
                sale_id.message_post(body=self.name, subject="Approval request refused")
                sale_id.button_refused()
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
