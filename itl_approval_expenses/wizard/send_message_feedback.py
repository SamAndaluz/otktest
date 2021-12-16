from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SendMessageFeedback(models.TransientModel):
    _name = 'send.message.feedback.expenses'
    _description = "Send Message Feedback Expenses"
    
    name = fields.Char(string="Reason")
    
    def send_message(self):
        if not self.name:
            raise UserError("Debe agregar un mensaje.")
        context = dict(self._context or {})
        
        approval_request_id = self.env['approval.request'].browse(context['active_id'])
        approval_request_id.action_refuse_confirm()
        
        if 'expense_sheet_id' in context:
            expense_sheet_id = self.env['hr.expense.sheet'].browse(context['expense_sheet_id'])
            if expense_sheet_id:
                expense_sheet_id.message_post(body=self.name, subject="Approval request refused")
                expense_sheet_id.refuse_sheet(self.name)
                approval_request_id.message_post(body=self.name, subject="Approval request refused")
