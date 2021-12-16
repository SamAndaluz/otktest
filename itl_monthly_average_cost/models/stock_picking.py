from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    
    itl_journal_entry_id = fields.Many2one('account.move', string="Temporal journal entry")
    itl_reversal_journal_entry_id = fields.Many2one('account.move', string="Reversal journal entry")
    itl_create_journal_in_receipt = fields.Boolean(related="partner_id.itl_create_journal_in_receipt")
    itl_hide_validate_button1 = fields.Boolean(compute="_check_if_hide_validate_button1")
    itl_hide_validate_button2 = fields.Boolean(compute="_check_if_hide_validate_button2")
    
    def _check_if_hide_validate_button1(self):
        _logger.info("***> _check_if_hide_validate_button1")
        self.itl_hide_validate_button1 = False
        if self.picking_type_code == 'incoming':
            if self.partner_id.itl_create_journal_in_receipt:
                if self.state in ['waiting','confirmed'] or not self.show_validate or not self.itl_journal_entry_id or not self.itl_reversal_journal_entry_id:
                    self.itl_hide_validate_button1 = True
            else:
                if self.state in ['waiting','confirmed'] or not self.show_validate:
                    self.itl_hide_validate_button1 = True
        else:
            _logger.info("***> else1")
            if self.state in ['waiting','confirmed'] or not self.show_validate:
                _logger.info("***> entró else1")
                self.itl_hide_validate_button1 = True
    
    def _check_if_hide_validate_button2(self):
        _logger.info("***> _check_if_hide_validate_button2")
        self.itl_hide_validate_button2 = False
        if self.picking_type_code == 'incoming':
            if self.partner_id.itl_create_journal_in_receipt:
                if self.state in ['waiting','confirmed'] or not self.show_validate or not self.itl_journal_entry_id or not self.itl_reversal_journal_entry_id:
                    self.itl_hide_validate_button2 = True
            else:
                if self.state in ['waiting','confirmed'] or not self.show_validate:
                    self.itl_hide_validate_button2 = True
        else:
            _logger.info("***> else2")
            if self.state not in ['waiting','confirmed'] or not self.show_validate:
                _logger.info("***> entró else2")
                self.itl_hide_validate_button2 = True
        
            
    def create_journal_entry(self):
        journal_id = self.company_id.itl_journal_id
        debit_account_id = self.company_id.itl_debit_account
        credit_account = self.company_id.itl_credit_account
        
        AccountMove = self.env['account.move']
        
        vals = {
            'ref': 'Póliza temporal ' + str(self.name),
            'journal_id': journal_id.id
        }
        
        AccountMoveLine = self.env['account.move.line']
        
        lines = []
        company_id = self.company_id
        currency_id = self.purchase_id.currency_id
            
        amount_currency = self.purchase_id.amount_total
        debit, credit2 = AccountMoveLine.itl_recompute_debit_credit_from_amount_currency(amount_currency, currency_id, company_id)
        debit2, credit = AccountMoveLine.itl_recompute_debit_credit_from_amount_currency(amount_currency * -1, currency_id, company_id)
        
        if company_id.currency_id != currency_id:
            currency_id = currency_id.id
        else:
            currency_id = False
        
        for line in self.move_line_ids_without_package:
            val_line = {
                'account_id': debit_account_id.id,
                'partner_id': self.partner_id.id,
                'name': str(self.name) + ' - ' + str(line.product_id.name),
                'currency_id': currency_id,
                'amount_currency': amount_currency,
                'debit': debit
            }
            lines.append((0, 0, val_line))
        
        for line in self.move_line_ids_without_package:
            val_line = {
                'account_id': credit_account.id,
                'partner_id': self.partner_id.id,
                'name': str(self.name) + ' - ' + str(line.product_id.name),
                'currency_id': currency_id,
                'amount_currency': amount_currency * -1,
                'credit': credit
            }
            lines.append((0, 0, val_line))
            
        vals.update(line_ids=lines)
        move_id = AccountMove.create(vals)
        
        move_id.action_post()
        
        self.itl_journal_entry_id = move_id.id
        
    def reverse_journal_entry(self):
        AccountMoveReversal = self.env['account.move.reversal']
        
        vals = {
            'move_id': self.itl_journal_entry_id.id,
            'date': self.itl_journal_entry_id.date,
            'refund_method': 'cancel',
            'residual': 0,
            'currency_id': self.purchase_id.currency_id.id,
            'move_type': 'entry'
        }
        
        amr_id = AccountMoveReversal.create(vals)
        moves_to_redirect = amr_id.itl_reverse_moves()
        #moves_to_redirect.action_post()
        
        self.itl_reversal_journal_entry_id = moves_to_redirect.id