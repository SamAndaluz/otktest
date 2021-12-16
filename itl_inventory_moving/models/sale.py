from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    itl_sale_origin_id = fields.Many2one('sale.order', string="Sale Origin")
    itl_is_rme = fields.Boolean(related="type_id.itl_is_rme")
    itl_warehouse_return_id = fields.Many2one('stock.warehouse', string="Destination Warehouse")
    
    def load_so(self):
        if self.itl_sale_origin_id:
            self.order_line.unlink()
            new_lines = []
            for line in self.itl_sale_origin_id.order_line:
                n_line = line.copy(default={'order_id': self.id})
            #self.order_line = [(4, new_lines)]
    
    
    @api.depends('order_line.qty_delivered')
    def _get_delivery_status(self):
        """ compute over all delivery status From line.
        """
        for order in self:
            deliver_quantity = sum(
                order.mapped('order_line').filtered(lambda r: r.product_id.type != 'service').mapped('qty_delivered'))
            order_quantity = sum(
                order.mapped('order_line').filtered(lambda r: r.product_id.type != 'service').mapped('product_uom_qty'))
            if order_quantity > deliver_quantity > 0:
                order.itl_delivery_status = 'partially delivered'
            elif order_quantity <= deliver_quantity > 0:
                order.itl_delivery_status = 'delivered'
            else:
                order.itl_delivery_status = 'not delivered'


    itl_delivery_status = fields.Selection([
        ('not delivered', 'Not Delivered'),
        ('partially delivered', 'Partially Delivered'),
        ('delivered', 'Fully Delivered')
    ], string='Delivery Status', compute="_get_delivery_status", store=True, readonly=True)
    
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    itl_is_rme = fields.Boolean(related="order_id.itl_is_rme")