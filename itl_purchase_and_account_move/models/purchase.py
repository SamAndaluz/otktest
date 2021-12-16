# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    received_products = fields.Boolean(string="Products have been received", compute="_get_received_product", store=False, copy=False)
    received_products_manual = fields.Boolean(string="Services have been received", copy=False, track_visibility='onchange')
    user_change_received_products = fields.Many2one('res.users', string="Last user that change Products have been received checkbox", readonly=True, store=True)
    has_services = fields.Boolean(string="Has services", compute="_get_received_product", store=False, copy=False)
    has_products = fields.Boolean(string="Has products", compute="_get_received_product", store=False, copy=False)
    
    @api.onchange('received_products_manual')
    def _onchange_received_products_manual(self):
        _logger.info("-> onchange received_products_manual")
        self.user_change_received_products = self.env.uid
            

    #@api.depends('picking_count')
    def _get_received_product(self):
        for purchase in self:
            purchase.has_services = False
            purchase.has_products = False
            received = True
            for pl in purchase.order_line:
                if pl.product_id.type in ['service','consu']:
                    purchase.has_services = True
                if pl.product_id.type in ['product']:
                    purchase.has_products = True
                    if pl.qty_received == 0:
                        received = False
            if not purchase.has_products:
                received = False
            if purchase.has_products and received:
                purchase.received_products = True
            else:
                purchase.received_products = False
            
class PurchaseOrderLineCustom(models.Model):
    _inherit = 'purchase.order.line'
    
    
    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel','draft']:
                    if inv_line.move_id.type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty