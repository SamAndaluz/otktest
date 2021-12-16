from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def post(self):
        res = super(AccountMove, self).post()
        
        for move in self:
            if move.sale_type_id.sale_type_account:
                expense_line_ids = move.line_ids.filtered(lambda i: i.product_id and i.debit > 0)
                for line in expense_line_ids:
                    line.account_id = move.sale_type_id.sale_type_account

        return res