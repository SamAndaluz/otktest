from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_uom_tax_ids = fields.Many2many('itl.uom.tax')
    
class ItlUomTax(models.Model):
    _name = 'itl.uom.tax'
    
    itl_uom_id = fields.Many2one('uom.uom', string="Unit of mesure")
    itl_tax_id = fields.Many2one('account.tax', string="Tax")