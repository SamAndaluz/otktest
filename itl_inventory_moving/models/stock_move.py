from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from itertools import groupby

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"
    
            
    def action_back_to_draft(self):
        if self.filtered(lambda m: m.state != "cancel"):
            raise UserError(_("You can set to draft cancelled moves only"))
        self.write({"state": "draft"})
        
        
    # Inherit from stock_account
    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        # For internal transfer, from warehouse A to B
        if self.picking_id.itl_transfer_origin:
            self.ensure_one()

            # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
            # the company currency... so we need to use round() before creating the accounting entries.
            ### Original values
            #debit_value = self.company_id.currency_id.round(cost)
            #credit_value = debit_value
            ## Invert values
            credit_value = self.company_id.currency_id.round(cost)
            debit_value = credit_value
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            credit_account_id = acc_dest
            valuation_partner_id = self._get_partner_id_for_valuation_lines()
            res = [(0, 0, line_vals) for line_vals in self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description).values()]
        else:
            res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        
        return res
    
        
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    return_lot_ids = fields.Many2many('stock.production.lot', compute='_get_return_lot')
    
    def _get_return_lot(self):
        for rec in self:
            returned_move_id = rec.move_id.origin_returned_move_id
            another_returned_move_id = rec.move_id.mapped('move_line_ids').mapped('lot_id')
            if returned_move_id:
                ids = []
                for line in returned_move_id.move_line_ids:
                    ids.append(line.lot_id.id)
                if ids:
                    for id in ids:
                        rec.return_lot_ids = [(4, id)]
            elif another_returned_move_id:
                rec.return_lot_ids = [(6,0, another_returned_move_id.ids)]
            else:
                ids = self.env['stock.production.lot'].search([('product_id', '=', rec.product_id.id)])
                rec.return_lot_ids = [(4, id.id) for id in ids]