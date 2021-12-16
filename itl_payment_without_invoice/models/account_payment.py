from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):
    _inherit = "account.payment"
    
    
    itl_purchase_id = fields.Many2one('purchase.order', string="Purchase Order", copy=False)
    itl_document_type = fields.Selection([('pediment','Pedimento'),('foreing_invoice','Factura extranjera')], related='itl_purchase_id.itl_document_type', string="Tipo de documento")
    itl_foreing_invoice = fields.Char(related='itl_purchase_id.itl_foreing_invoice', string="Número de factura extranjera", copy=False)
    itl_pediment = fields.Char(related='itl_purchase_id.itl_pediment', help='Optional field for entering the customs information in the case '
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
        string='Pediment', size=21, copy=False)
    
    _sql_constraints = [
        ('itl_pediment',
         'unique (itl_pediment)',
         _('The pediment number is being used in other payment request!')),
        ('itl_foreing_invoice',
         'unique (itl_foreing_invoice)',
         _('The foreing invoice number is being used in other payment request!'))
    ]
    
    @api.model
    def default_get(self, default_fields):
        rec = super(account_payment, self).default_get(default_fields)
        
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        
        purchase_id = self.env[active_model].browse(active_ids)
        acc_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('company_id', '=', self.env.company.id), ('currency_id.name','=','MXN')], limit=1)
        
        rec.update({
            'currency_id': acc_journal.currency_id.id,
            'payment_type': 'outbound',
            'itl_purchase_id': purchase_id.id,
            'partner_id': purchase_id.partner_id.id,
            'amount': abs(purchase_id.amount_total),
            'journal_id': acc_journal.id
        })
        
        return rec
    
    @api.onchange('currency_id')
    def _onchange_currency(self):
        rec = super(account_payment, self)._onchange_currency()
        
        if self.itl_purchase_id:
            self.amount = abs(self.itl_purchase_id.amount_total)
        
        return rec
        
    def post(self):
        rec = super(account_payment, self).post()
        
        for payment in self:
            if payment.itl_purchase_id:
                payment.itl_purchase_id.itl_payment_id = payment
        
        return rec