from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import re

import logging
_logger = logging.getLogger(__name__)

class PaymentRequest(models.TransientModel):
    _inherit = 'itl.payment.request'
    
    __pattern = re.compile(r'[0-9]{2}  [0-9]{2}  [0-9]{4}  [0-9]{7}')
    
    itl_is_payment_control = fields.Boolean(string="Payment control w/o invoice")
    itl_document_type = fields.Selection([('pediment','Pedimento'),('foreing_invoice','Foreing invoice')], string="Document type")
    itl_foreing_invoice = fields.Char(string="Foreing invoice number", copy=False)
    itl_pediment = fields.Char(help='Optional field for entering the customs information in the case '
        'of first-hand sales of imported goods or in the case of foreign trade'
        ' operations with goods or services.\n'
        'The format must be:\n'
        ' - 2 digits of the year of validation followed by two spaces.\n'
        ' - 2 digits of customs clearance followed by two spaces.\n'
        ' - 4 digits of the serial number followed by two spaces.\n'
        ' - 1 digit corresponding to the last digit of the current year, '
        'except in case of a consolidated customs initiated in the previous '
        'year of the original request for a rectification.\n'
        ' - 6 digits of the progressive numbering of the custom.',
        string='Pedimento', size=21, copy=False)
    
    @api.constrains('itl_pediment')
    def check_pediment_format(self):
        help_message = self.fields_get().get(
            "itl_pediment").get("help").split('\n', 1)[1]
        for rec in self.filtered('itl_pediment'):
            if not self.__pattern.match(rec.itl_pediment):
                raise ValidationError(_(
                    'Error!, The format of the pediment is'
                    ' incorrect. \n%s\n'
                    'For example: 15  48  3009  0001234') % (help_message))
        
        
    @api.onchange('itl_document_type')
    def _onchange_itl_document_type(self):
        self.itl_foreing_invoice = False
        self.itl_pediment = False
        
    @api.onchange('itl_is_payment_control')
    def _onchange_itl_document_type(self):
        self.itl_document_type = False
        self.itl_foreing_invoice = False
        self.itl_pediment = False
    
    def send_request(self):
        super(PaymentRequest, self).send_request()
        
        payment_control_id = False
        if self.itl_document_type:
            vals = {
                'itl_document_type': self.itl_document_type,
                'itl_foreing_invoice': self.itl_foreing_invoice,
                'itl_pediment': self.itl_pediment
            }
            
            payment_control_id = self.env['itl.payment.control'].create(vals)
        
        if self.purchase_order_id:
            if payment_control_id:
                self.purchase_order_id.itl_payment_control_id = payment_control_id
                payment_control_id.itl_purchase_id = self.purchase_order_id
                self.purchase_order_id.payment_approval_id.itl_payment_control_id = payment_control_id
            