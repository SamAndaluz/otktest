# -*- coding: utf-8 -*-
from odoo import models, fields, api
import re

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    def _get_payment_method(self):
        return self.env.company.itl_payment_method_id
    
    def _get_property_payment_term_id(self):
        return self.env.company.it_property_payment_term_id
    
    def _get_usage(self):
        return self.env.company.itl_usage
    
    
    itl_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method', "Forma de pago", default=_get_payment_method)
    itl_usage = fields.Selection([
        ('G01', 'Acquisition of merchandise'),
        ('G02', 'Returns, discounts or bonuses'),
        ('G03', 'General expenses'),
        ('I01', 'Constructions'),
        ('I02', 'Office furniture and equipment investment'),
        ('I03', 'Transportation equipment'),
        ('I04', 'Computer equipment and accessories'),
        ('I05', 'Dices, dies, molds, matrices and tooling'),
        ('I06', 'Telephone communications'),
        ('I07', 'Satellite communications'),
        ('I08', 'Other machinery and equipment'),
        ('D01', 'Medical, dental and hospital expenses.'),
        ('D02', 'Medical expenses for disability'),
        ('D03', 'Funeral expenses'),
        ('D04', 'Donations'),
        ('D05', 'Real interest effectively paid for mortgage loans (room house)'),
        ('D06', 'Voluntary contributions to SAR'),
        ('D07', 'Medical insurance premiums'),
        ('D08', 'Mandatory School Transportation Expenses'),
        ('D09', 'Deposits in savings accounts, premiums based on pension plans.'),
        ('D10', 'Payments for educational services (Colegiatura)'),
        ('P01', 'To define'),
    ], 'Uso de CFDI', default=_get_usage,
        help='Used in CFDI 3.3 to express the key to the usage that will '
        'gives the receiver to this invoice. This value is defined by the '
        'customer. \nNote: It is not cause for cancellation if the key set is '
        'not the usage that will give the receiver of the document.')
    itl_is_invoice_required = fields.Boolean("Requiere factura", required=True)
    
    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,
        string='Customer Payment Terms',
        help="This payment term will be used instead of the default one for sales orders and customer invoices",
        default=_get_property_payment_term_id)
    #temporal_vat = fields.Char("RFC temporal")
    
    @api.onchange('itl_is_invoice_required')
    def _onchange_itl_is_invoice_required(self):
        if not self.itl_is_invoice_required:
            _logger.info("itl_payment_method_id: " + str(self.env.company.itl_payment_method_id))
            self.itl_payment_method_id = self.env.company.itl_payment_method_id
            self.itl_usage = self.env.company.itl_usage
            self.property_payment_term_id = self.env.company.it_property_payment_term_id
        else:
            self.itl_payment_method_id = False
            self.itl_usage = False
            self.property_payment_term_id = False
            
    def validate_rfc(self, rfc):
        _logger.info("--> rfc: " + str(rfc))
        pattern = re.compile("^([A-ZÑ&]{3,4}) ?(?:- ?)?(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])) ?(?:- ?)?([A-Z\d]{2})([A\d])$")

        return True if pattern.match(rfc) != None else False