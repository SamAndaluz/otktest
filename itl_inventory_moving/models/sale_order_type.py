from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"
    
    itl_is_rme = fields.Boolean(string="Is RME")