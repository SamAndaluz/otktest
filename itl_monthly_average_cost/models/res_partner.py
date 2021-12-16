from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    
    itl_create_journal_in_receipt = fields.Boolean(string="Crear journal entry temporal en recepción")