from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    itl_move_ids = fields.Many2many('account.move', 'move_itl_move', 'move_id', 'itl_move_id', string="Journal entries related", compute="_get_journal_entries")
    
    
    def _get_journal_entries(self):
        for move in self:
            move.itl_move_ids = []
            move_ids = self.env['account.move'].search([('line_ids.name','=',move.name)])
            if len(move_ids) > 0:
                move.itl_move_ids = move_ids.filtered(lambda m: m.name != move.name)
    