from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class ItlChangeWarehouse(models.TransientModel):
    _name = "itl.change.warehouse"
    _description = "Change warehouse"
    
    
    itl_warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    itl_picking_type_id = fields.Many2one("stock.picking.type", string="Operation Type")
    itl_location_id = fields.Many2one("stock.location", string="Soruce Location")
    itl_location_dest_id = fields.Many2one("stock.location", string="Destination Location")
    
    
    @api.onchange('itl_warehouse_id')
    def _onchange_itl_warehouse_id(self):
        if self.itl_warehouse_id:
            p_ids =  self.env.context.get('picking_ids')
            picking_ids = self.env['stock.picking'].browse(p_ids)
            for picking in picking_ids:
                if picking.picking_type_code == 'internal':
                    if picking.location_id.name == 'Stock' and picking.location_dest_id.name == 'Output':
                        code = 'outgoing'
                if picking.picking_type_code == 'outgoing':
                    code = 'outgoing'
                if picking.picking_type_code == 'incoming':
                    code = 'incoming'
                picking_type_id = self.env['stock.picking.type'].search([('code','=',code),('warehouse_id','=',self.itl_warehouse_id.id)])
                if picking_type_id:
                    self.itl_picking_type_id = picking_type_id[0]

                
    @api.onchange('itl_picking_type_id')
    def onchange_picking_type(self):
        if self.itl_picking_type_id:
            if self.itl_picking_type_id.default_location_src_id:
                location_id = self.itl_picking_type_id.default_location_src_id.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.itl_picking_type_id.default_location_dest_id:
                location_dest_id = self.itl_picking_type_id.default_location_dest_id.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()

            self.itl_location_id = location_id
            self.itl_location_dest_id = location_dest_id
            
    def action_confirm(self):
        p_ids =  self.env.context.get('picking_ids')
        picking_ids = self.env['stock.picking'].browse(p_ids)
        for picking in picking_ids:
            if picking.picking_type_code == 'outgoing' or (picking.picking_type_code == 'internal' and picking.location_id.name == 'Stock' and picking.location_dest_id.name == 'Output'):
                if len(picking.move_line_ids_without_package) > 0:
                    product_ids = picking.move_line_ids_without_package.mapped("product_id")

                    #list_reserved = []
                    #for p in product_ids:
                    #    reserved = sum(picking_id.move_line_ids_without_package.filtered(lambda i: i.product_id.id == p.id).mapped('product_uom_qty'))
                    #    values = {'id': p.id, 'reserved': reserved}
                    #    list_reserved.append(values)

                    #for lr in list_reserved:
                    #    product_id = self.env['product.product'].browse(lr['id'])
                    #    available_quantity = product_id.with_context(itl_warehouse_id=self.itl_warehouse_id.id)._get_warehouse_quantity()

                    #    if available_quantity < lr['reserved']:
                    #        raise ValidationError("The warehouse %s doesn't has enough quantity for %s." % (self.itl_warehouse_id.name, product_id.name))

                    picking.action_cancel()
                    picking.action_back_to_draft()
                    #picking_id.operating_unit_id = self.itl_warehouse_id.operating_unit_id
                    picking.picking_type_id = self.itl_picking_type_id
                    picking.location_id = self.itl_location_id
                    picking.location_dest_id = self.itl_location_dest_id
                    picking._onchange_location_id()
                    picking._autoconfirm_picking()
                    picking.action_assign()
                else:
                    picking.action_back_to_draft()
                    picking.picking_type_id = self.itl_picking_type_id
                    picking.location_id = self.itl_location_id
                    picking.location_dest_id = self.itl_location_dest_id

                if picking.sale_id:
                    picking.sale_id.warehouse_id = self.itl_warehouse_id
                    if not picking.move_ids_without_package.mapped('sale_line_id'):
                        for line in picking.sale_id.order_line:
                            move_id = picking.move_ids_without_package.filtered(lambda m: m.product_id == line.product_id)
                            for m in move_id:
                                move_id.sale_line_id = line
                        
            if picking.picking_type_code == 'incoming':
                picking.action_cancel()
                picking.action_back_to_draft()
                #picking_id.operating_unit_id = self.itl_warehouse_id.operating_unit_id
                picking.picking_type_id = self.itl_picking_type_id
                picking.location_id = self.itl_location_id
                picking.location_dest_id = self.itl_location_dest_id
                picking._autoconfirm_picking()
                picking.action_assign()
                if picking.purchase_id:
                    picking.purchase_id.picking_type_id  = self.itl_picking_type_id
                    