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
    
    lot_id_domain = fields.Char(
       compute="_compute_lot_id_domain",
       readonly=True,
       store=False,
   )
    
    itl_delivery_by = fields.Selection(related="picking_id.itl_delivery_by")
    itl_logistic_company_id = fields.Many2one(related="picking_id.itl_logistic_company_id")
    itl_employee_partner_id = fields.Many2one(related="picking_id.itl_employee_partner_id")
    
    @api.depends('product_id')
    def _compute_lot_id_domain(self):
        for rec in self:
            if rec.picking_code != 'incoming':
                rec.lot_id_domain = json.dumps(
                   [('product_id','=', rec.product_id.id), ('company_id', '=', rec.company_id.id), ('itl_location_ids', 'child_of', rec.location_id.id)]
                )
            else:
                rec.lot_id_domain = json.dumps(
                   [('product_id','=', rec.product_id.id), ('company_id', '=', rec.company_id.id)]
                )