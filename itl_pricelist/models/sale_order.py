
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    itl_product_sale_ok = fields.Boolean(related='product_id.sale_ok')
    itl_product_type = fields.Selection(related='product_id.type')