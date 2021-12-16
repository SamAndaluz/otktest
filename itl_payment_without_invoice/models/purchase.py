from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    payment_requests_status = fields.Selection(selection_add=[('payment_without_invoice','Payment without invoice')])
    
    itl_payment_control_id = fields.Many2one('itl.payment.control', copy=False, string="Payment control", ondelete="cascade")
    
    itl_document_type = fields.Selection([('pediment','Pedimento'),('foreing_invoice','Foreing invoice')], string="Document type", related="itl_payment_control_id.itl_document_type")
    itl_foreing_invoice = fields.Char(string="Foreing invoice number", related="itl_payment_control_id.itl_foreing_invoice")
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
        string='Pedimento', size=21, related="itl_payment_control_id.itl_pediment")
    
    def action_register_payment(self):
        self = self.with_context(active_id=self.id)
        payment = self.env['purchase.advance.payment.inv']
        
        if self.itl_document_type == 'pediment':
            purchase_deposit_product_id = int(self.env['ir.config_parameter'].sudo().get_param('itl_ped_purchase_deposit_default_product_id'))
        else:
            purchase_deposit_product_id = int(self.env['ir.config_parameter'].sudo().get_param('itl_inv_purchase_deposit_default_product_id'))
        
        vals = {
            'advance_payment_method': 'fixed',
            'amount': self.amount_total,
            'purchase_deposit_product_id': purchase_deposit_product_id
        }
        
        p = payment.create(vals)
        invoices = p.with_context({'active_ids': self.id}).itl_create_invoices()
        
        for invoice in invoices:
            self.itl_payment_control_id.itl_advance_bill_id = invoice
            invoice.itl_is_advance_payment = True
            invoice.action_post()
        
