from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
import json
from json import dumps

class AccountMove(models.Model):
    _inherit = "account.move"
    
    has_expense = fields.Boolean()
    expense_id = fields.Many2one('hr.expense', string="Expense")
    sheet_id = fields.Many2one(related="expense_id.sheet_id")
    advance_sheet_id = fields.Many2one(related="expense_id.sheet_id.advance_sheet_id")
    payment_id = fields.Many2one('account.payment', compute="_get_payment")
    payment_date = fields.Date(related="payment_id.payment_date")
    
    invoice_expenses_widget = fields.Text(groups="account.group_account_invoice",
        compute='_compute_expense_widget_reconciled_info')
    
    
    def _get_payment(self):
        self.payment_id = False
        if self.advance_sheet_id:
            self.payment_id = self.advance_sheet_id.itl_payment_ids[0].id
    
    @api.depends('type', 'expense_id')
    def _compute_expense_widget_reconciled_info(self):
        for move in self:
            reconciled_vals = move._get_expense_reconciled_info_JSON_values()
            if reconciled_vals:
                info = {
                    'title': _('Less Payment'),
                    'outstanding': False,
                    'content': reconciled_vals,
                }
                move.invoice_expenses_widget = json.dumps(info, default=date_utils.json_default)
            else:
                move.invoice_expenses_widget = json.dumps(False)
                
    def _get_expense_reconciled_info_JSON_values(self):
        self.ensure_one()
        reconciled_vals = []
        aml = self.env['account.move.line'].search([('move_id','=',self.expense_id.sheet_id.advance_sheet_id.itl_payment_ids[0].id)])
        credit_line = aml.filtered(lambda i: i.credit != 0)
        ref = credit_line.move_id.name
        if credit_line.move_id.ref:
            ref += ' (' + credit_line.move_id.ref + ')'

        reconciled_vals.append({
            'name': 'Expense Payment: ' + self.name,
            'journal_name': self.expense_id.sheet_id.advance_sheet_id.itl_payment_ids[0].journal_id.name,
            'amount': self.expense_id.total_amount,
            'currency': self.currency_id.symbol,
            'digits': [69, self.currency_id.decimal_places],
            'position': self.currency_id.position,
            'date': self.expense_id.date,
            'payment_id': credit_line.id,
            'account_payment_id': credit_line.payment_id.id,
            'payment_method_name': credit_line.payment_id.payment_method_id.name if credit_line.journal_id.type == 'bank' else None,
            'move_id': credit_line.move_id.id,
            'ref': ref,
        })
        return reconciled_vals
        
    
    # Inherit
    def _compute_payments_widget_to_reconcile_info(self):
        for move in self:
            move.invoice_outstanding_credits_debits_widget = json.dumps(False)
            move.invoice_has_outstanding = False

            if move.state != 'posted' or move.invoice_payment_state != 'not_paid' or not move.is_invoice(include_receipts=True):
                continue
            pay_term_line_ids = move.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            
            # Adding extra condition for Expenses journal
            expense_journal_id = move.company_id.itl_special_expense_journal_id
            domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                      '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'), ('journal_id.post_at', '=', 'bank_rec'),
                      ('partner_id', '=', move.commercial_partner_id.id),
                      ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0),('journal_id','!=',expense_journal_id.id)]

            if move.is_inbound():
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'move_id': move.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = move.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == move.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
                                                           line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, move.currency_id.decimal_places],
                        'payment_date': fields.Date.to_string(line.date),
                    })
                info['title'] = type_payment
                _logger.info("##### info: " + str(info))
                move.invoice_outstanding_credits_debits_widget = json.dumps(info)
                move.invoice_has_outstanding = True