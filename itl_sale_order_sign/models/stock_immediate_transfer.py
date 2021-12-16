# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    pick_ids = fields.Many2many('stock.picking', 'stock_picking_transfer_rel')

    def itl_process(self):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']
        for picking in self.pick_ids:
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        _logger.info("--> pick_to_do: " + str(pick_to_do))
        if pick_to_do:
            pick_to_do.action_done()
        return False
