from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_uom_tax_ids = fields.Many2many(related="company_id.itl_uom_tax_ids", readonly=False)