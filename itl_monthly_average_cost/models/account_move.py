
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

#forbidden fields
INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def itl_recompute_debit_credit_from_amount_currency(self, amount_currency, currency_id, company_id):
        # Recompute the debit/credit based on amount_currency/currency_id and date.

        company_currency = company_id.currency_id
        balance = amount_currency
        if currency_id and company_currency and currency_id != company_currency:
            balance = currency_id._convert(balance, company_currency, company_id, fields.Date.today())
            debit = balance > 0 and balance or 0.0
            credit = balance < 0 and -balance or 0.0
                
            return debit, credit
        return False, False