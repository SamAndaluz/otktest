# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.product"

    #warehouse_quantity = fields.Char(compute='_get_warehouse_quantity', string='Quantity per warehouse')

    def _get_warehouse_quantity(self):
        warehouse_quantity_text = ''
        itl_warehouse_id = self.env.context.get('itl_warehouse_id')
        
        quant_ids = self.env['stock.quant'].sudo().search([('product_id','=',self.id),('location_id.usage','=','internal')])
        t_warehouses = {}
        for quant in quant_ids:
            if quant.location_id:
                if quant.location_id not in t_warehouses:
                    t_warehouses.update({quant.location_id:0})
                t_warehouses[quant.location_id] += (quant.quantity - quant.reserved_quantity)
        _logger.info("## t_warehouses: " + str(t_warehouses))
        tt_warehouses = {}
        for location in t_warehouses:
            warehouse = False
            location1 = location
            while (not warehouse and location1):
                warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',location1.id)])
                if len(warehouse_id) > 0:
                    warehouse = True
                else:
                    warehouse = False
                location1 = location1.location_id
            if warehouse_id:
                if warehouse_id.id not in tt_warehouses:
                    tt_warehouses.update({warehouse_id.id:0})
                tt_warehouses[warehouse_id.id] += t_warehouses[location]

        #_logger.info("### Available quantity: " + str(tt_warehouses[itl_warehouse_id]))
        #raise ValidationError("Testing...")
        if itl_warehouse_id not in tt_warehouses:
            return 0
        
        return tt_warehouses[itl_warehouse_id]