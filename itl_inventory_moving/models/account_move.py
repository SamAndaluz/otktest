from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import json
import re

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_payments_reconciled_info(self):
        if self.state != 'posted' or not self.is_invoice(include_receipts=True):
            return False
        reconciled_vals = self._get_reconciled_info_JSON_values()
        if reconciled_vals:
            info = {
                'title': _('Less Payment'),
                'outstanding': False,
                'content': reconciled_vals,
            }
            return info
        else:
            return False
        
    def _get_payments_widget_to_reconcile_info(self):

        if self.state != 'posted' or self.invoice_payment_state != 'not_paid' or not self.is_invoice(include_receipts=True):
            return False
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))

        domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                  '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'), ('journal_id.post_at', '=', 'bank_rec'),
                  ('partner_id', '=', self.commercial_partner_id.id),
                  ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                  ('amount_residual_currency', '!=', 0.0)]

        if self.is_inbound():
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
            type_payment = _('Outstanding credits')
        else:
            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
            type_payment = _('Outstanding debits')
        info = {'title': '', 'outstanding': True, 'content': [], 'move_id': self.id}
        lines = self.env['account.move.line'].search(domain)
        currency_id = self.currency_id
        if len(lines) != 0:
            for line in lines:
                # get the outstanding residual value in invoice currency
                if line.currency_id and line.currency_id == self.currency_id:
                    amount_to_show = abs(line.amount_residual_currency)
                else:
                    currency = line.company_id.currency_id
                    amount_to_show = currency._convert(abs(line.amount_residual), self.currency_id, self.company_id,
                                                       line.date or fields.Date.today())
                if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                    continue
                info['content'].append({
                    'journal_name': line.ref or line.move_id.name,
                    'amount': amount_to_show,
                    'currency': currency_id.symbol,
                    'id': line.id,
                    'position': currency_id.position,
                    'digits': [69, self.currency_id.decimal_places],
                    'payment_date': fields.Date.to_string(line.date),
                })
            info['title'] = type_payment
            return info
    
    def _get_reversal_move_line(self):
        pay_term_line_ids = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
        domain = [('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
                      '|', ('move_id.state', '=', 'posted'), '&', ('move_id.state', '=', 'draft'), ('journal_id.post_at', '=', 'bank_rec'),
                      ('partner_id', '=', self.commercial_partner_id.id),
                      ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
                      ('amount_residual_currency', '!=', 0.0)]
        if self.is_inbound():
            domain.extend([('credit', '>', 0), ('debit', '=', 0)])
        else:
            domain.extend([('credit', '=', 0), ('debit', '>', 0)])
        lines = self.env['account.move.line'].search(domain)
        return lines
    
        

        
            
