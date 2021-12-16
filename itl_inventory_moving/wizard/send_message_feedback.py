from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback'
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        approval_request_id.action_refuse_confirm()
        
        if 'sale_id' in context:
            stock_picking_id = self.env['stock.picking'].sudo().browse(context['stock_picking_id'])
            if stock_picking_id:
                stock_picking_id.message_post(body=self.name, subject="Approval request refused")
                stock_picking_id.button_refused()
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
