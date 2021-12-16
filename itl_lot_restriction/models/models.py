from collections import Counter

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
import json

import logging
_logger = logging.getLogger(__name__)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    itl_product_uom_qty = fields.Float(related="move_id.product_uom_qty")
    
    def show_all_lots(self):
        view = self.env.ref('itl_lot_restriction.itl_view_stock_production_lot_all')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['product_id'] = self.product_id.id
        context['stock_move_line_id'] = self.id
        return {
            'name': 'More Lots',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.stock.production.lot.all',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }
    
    #@api.onchange('lot_id')
    #def onchange_lot_id(self):
    #    if self.picking_id:
    #        self.picking_id.action_assign()
    
class itlStockProductionLotAll(models.TransientModel):
    _name = "itl.stock.production.lot.all"
    _description = "Show All Lots"
    _rec_name = "id"
    
    
    @api.model
    def default_get(self, fields):
        res = super(itlStockProductionLotAll, self).default_get(fields)
        
        product_id = self.env['product.product'].browse(self.env.context.get('product_id'))
        sml_id = self.env['stock.move.line'].browse(self.env.context.get('stock_move_line_id'))
        
        if product_id:
            res['itl_product_id'] = product_id.id
            
        if sml_id:
            res['itl_stock_move_line_id'] = sml_id.id
            
        return res
    
    
    itl_lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")
    itl_product_id = fields.Many2one('product.product', string="Product")
    itl_stock_move_line_id = fields.Many2one('stock.move.line', string="Stock Move Line")
    
    
    def use_lot(self):
        self.sudo().itl_stock_move_line_id.lot_id = self.itl_lot_id
        context = dict(self._context or {})
        
        if 'from_prepare_picking' in context and context.get('from_prepare_picking') == True:
            flag = self.env.user.has_group('itl_inventory_moving.group_itl_prepare_picking')
            if not flag:
                raise ValidationError("You are not allowed to prepare movements.")
            view = self.env.ref('itl_inventory_moving.itl_prepare_picking_form')
            view_id = view and view.id or False
            context = dict(self._context or {})

            return {
                'name': 'Prepare picking',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'itl.prepare.picking',
                'res_id': context['pp_id'],
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        
        if 'from_prepare_picking_2' in context and context.get('from_prepare_picking_2') == True:
            flag = self.env.user.has_group('itl_inventory_moving.group_itl_validate_picking')
            if not flag:
                raise ValidationError("You are not allowed to prepare movements.")
            view = self.env.ref('itl_inventory_moving.itl_prepare_picking_2_form')
            view_id = view and view.id or False
            context = dict(self._context or {})

            return {
                'name': 'Prepare picking',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'itl.prepare.picking.two',
                'res_id': context['pp_id'],
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context,
                'flags': {'form': {'action_buttons': False}}
            }
        
        
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _order = 'create_date desc'
        
    