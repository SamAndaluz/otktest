# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError,UserError
from odoo.addons import decimal_precision as dp

class legacy_invoice_product(models.Model):
    _name = 'legacy.invoice.product'
    _description = "ITL Legacy Invoice Product"
    
    name = fields.Char(string="Nombre", required=True)
    price = fields.Float(string="Precio de venta")
    standard_price = fields.Float('Coste', company_dependent=True, digits=dp.get_precision('Product Price'))
    default_code = fields.Char('Internal Reference', index=True)
    type = fields.Selection([('consu','Consumible'),
                             ('service','Servicio'),
                             ('product','Almacenable')])
    l10n_mx_edi_code_sat_id = fields.Many2one('l10n_mx_edi.product.sat.code', string="Código SAT")
    uom_id = fields.Many2one('uom.uom', string="Unidad de medida")
    uom_po_id = fields.Many2one('uom.uom', string="Unidad de medida compra")
    
    #account_move = fields.Many2one('account.move', string="Factura")