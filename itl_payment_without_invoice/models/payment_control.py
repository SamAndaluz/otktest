from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from collections import defaultdict

import logging
_logger = logging.getLogger(__name__)

class PaymentControl(models.Model):
    _name = "itl.payment.control"
    
    itl_purchase_id = fields.Many2one('purchase.order', string="Purchase Order", copy=False)
    itl_bill_id = fields.Many2one('account.move', string="Bill", copy=False)
    itl_advance_bill_id = fields.Many2one('account.move', string="Down payment Bill", copy=False)
    itl_document_type = fields.Selection([('pediment','Pedimento'),('foreing_invoice','Factura extranjera')], string="Tipo de documento")
    itl_foreing_invoice = fields.Char(string="Número de factura extranjera", copy=False)
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
        string='Pediment', size=21, copy=False)
    itl_is_done = fields.Boolean(string="Is Done")
    
    _sql_constraints = [
        ('itl_pediment',
         'unique (itl_pediment)',
         _('The pediment number is being used in other payment request!')),
        ('itl_foreing_invoice',
         'unique (itl_foreing_invoice)',
         _('The foreing invoice number is being used in other payment request!'))
    ]
    
    
    @api.depends('itl_document_type')
    def name_get(self):
        self = self.sudo()
        result = []
        for record in self:
            if record.itl_document_type == 'pediment':
                name = '%s, %s, %s, %s%s' % (dict(record._fields['itl_document_type'].selection).get(record.itl_document_type), record.itl_pediment, record.itl_purchase_id.name, record.itl_purchase_id.currency_id.symbol, record.itl_purchase_id.amount_total)
            if record.itl_document_type == 'foreing_invoice':
                name = '%s, %s, %s, %s%s' % (dict(record._fields['itl_document_type'].selection).get(record.itl_document_type), record.itl_foreing_invoice, record.itl_purchase_id.name, record.itl_purchase_id.currency_id.symbol, record.itl_purchase_id.amount_total)
            result.append((record.id, name))
        return result