# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    def action_cancel(self):
        posted_invoices = self.invoice_ids.filtered(lambda inv: inv.state in ['posted'])
        if len(posted_invoices) > 0:
            raise ValidationError("No puede cancelar una orden de venta que tiene una o más facturas posteadas, cancele primero las facturas y después cancele la orden de venta.")
        
        return super(SaleOrder, self).action_cancel()

"""
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    itl_product_sale_ok = fields.Boolean(related='product_id.sale_ok')
    itl_product_type = fields.Selection(related='product_id.type')
"""