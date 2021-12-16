from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class account_payment(models.Model):
    _inherit = "account.payment"
    
    itl_destination_amount = fields.Monetary(string="Destination amount")
    itl_destination_currency = fields.Many2one('res.currency')
    
    itl_has_different_currencies = fields.Boolean(compute="_check_currencies")
    
    @api.onchange('journal_id','destination_journal_id')
    def _get_destination_currency(self):
        if self.destination_journal_id:
            self.itl_destination_currency = self.destination_journal_id.currency_id
            if self.journal_id.currency_id == self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                self.itl_destination_currency = self.company_id.currency_id
        
    
    @api.depends('journal_id','destination_journal_id')
    def _check_currencies(self):
        self.itl_has_different_currencies = False
        if self.payment_type == 'transfer':
            if self.journal_id.currency_id == self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                self.itl_has_different_currencies = False
                return
            if self.destination_journal_id.currency_id and self.journal_id.currency_id != self.destination_journal_id.currency_id:
                self.itl_has_different_currencies = True
                return
            if self.journal_id.currency_id == self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                self.itl_has_different_currencies = True
                return
    
    def _prepare_payment_moves(self):
        all_move_vals = super(account_payment, self)._prepare_payment_moves()
        if self.payment_type == 'transfer':
            if self.journal_id.currency_id == self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                return all_move_vals
            if self.journal_id.currency_id != self.destination_journal_id.currency_id and self.destination_journal_id.currency_id == self.company_id.currency_id:
                _logger.info("***> ENTRO")
                #pass
                #all_move_vals[0]['line_ids'][1][2]['amount_currency'] = all_move_vals[0]['line_ids'][1][2]['amount_currency'] * -1
                all_move_vals[0]['line_ids'][0][2]['debit'] = self.itl_destination_amount
                all_move_vals[0]['line_ids'][1][2]['credit'] = self.itl_destination_amount
                
                all_move_vals[1]['line_ids'][1][2]['currency_id'] = False
                all_move_vals[1]['line_ids'][1][2]['amount_currency'] = self.itl_destination_amount
                
                all_move_vals[1]['line_ids'][0][2]['credit'] = self.itl_destination_amount
                all_move_vals[1]['line_ids'][1][2]['debit'] = self.itl_destination_amount
                
            if self.journal_id.currency_id != self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                all_move_vals[1]['line_ids'][1][2]['amount_currency'] = self.itl_destination_amount
                
            if self.journal_id.currency_id == self.destination_journal_id.currency_id and self.destination_journal_id.currency_id != self.company_id.currency_id:
                all_move_vals[0]['line_ids'][0][2]['debit'] = self.itl_destination_amount
                all_move_vals[0]['line_ids'][1][2]['credit'] = self.itl_destination_amount
                
                all_move_vals[1]['line_ids'][0][2]['credit'] = self.itl_destination_amount
                all_move_vals[1]['line_ids'][1][2]['debit'] = self.itl_destination_amount
        
        _logger.info("---> all_move_vals: " + str(all_move_vals))
        #raise ValidationError("Testing...")
        return all_move_vals
    