from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Inherit from sale_stock
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        record = self.env.company.itl_user_warehouse_ids.filtered(lambda i: self.env.user.id in i.itl_user_ids.ids)
        if len(record) == 1:
            warehouse_ids = record.itl_warehouse_id
        return warehouse_ids
    
    # Inherit from sale_stock
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True)
    
    # Inherit from sale_stock
    @api.model
    def _onchange_company_id(self):
        if self.company_id:
            warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
            self.warehouse_id = warehouse_id or self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            record = self.company_id.itl_user_warehouse_ids.filtered(lambda i: self.env.user.id in i.itl_user_ids.ids)
            if len(record) == 1:
                self.warehouse_id = record.itl_warehouse_id
                
    @api.onchange('order_line')
    def check_qty(self):
        records = self.company_id.itl_user_warehouse_condition_ids.filtered(lambda i: self.env.user.id in i.itl_user_ids.ids)
        qty = 0
        for line in self.order_line:
            qty += line.product_uom_qty
        
        for r in records:
            if r.itl_condition == 'less_than' and qty <= r.itl_qty_condition:
                self.warehouse_id = r.itl_warehouse_id
            if r.itl_condition == 'greater_than' and qty >= r.itl_qty_condition:
                self.warehouse_id = r.itl_warehouse_id
                
        