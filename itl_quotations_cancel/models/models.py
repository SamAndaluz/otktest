# -*- coding: utf-8 -*-

# from odoo import models, fields, api
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class itl_quotations_cancel(models.Model):
    _inherit = 'sale.order'
    def metodo_prueba(self):
        self.write({'state': 'cancel'})

class itl_quotations_cancel_2(models.Model):
    _inherit = 'stock.picking'
    def itl_cancel_stock_picking(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'is_locked': True})

# class itl_quotations_cancel(models.Model):
#     _name = 'itl_quotations_cancel.itl_quotations_cancel'
#     _description = 'itl_quotations_cancel.itl_quotations_cancel'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
