from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class PaymentRequest(models.TransientModel):
    _name = 'itl.payment.request'
    _description = "Payment Request"
    
    
    itl_urgent_payment = fields.Boolean(string="Urgent payment")
    itl_payment_date = fields.Date(string="Payment date")
    itl_urgency_reason = fields.Text(string="Reason of urgent payment")
    purchase_order_id = fields.Many2one('purchase.order')
    
    
    @api.model
    def default_get(self, fields):
        res = super(PaymentRequest, self).default_get(fields)
        if self._context.get('active_id'):
            purchase_id = self.env['purchase.order'].browse(self._context.get('active_id'))
            if purchase_id:
                res['purchase_order_id'] = purchase_id.id
        return res 
        
        
    @api.onchange('itl_urgent_payment')
    def _onchange_itl_urgent_payment(self):
        self.itl_payment_date = False
        self.itl_urgency_reason = False
    
    def send_request(self):
        if self.purchase_order_id and self.itl_urgent_payment:
            self.purchase_order_id.itl_urgent_payment = self.itl_urgent_payment
            self.purchase_order_id.itl_payment_date = self.itl_payment_date
            self.purchase_order_id.itl_urgency_reason = self.itl_urgency_reason
            
        self.purchase_order_id.send_to_approve_request_payment()