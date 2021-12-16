# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


from werkzeug.urls import url_encode


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Inherit from sale module
    def _create_invoices(self, grouped=False, final=False):
        moves = super(SaleOrder, self)._create_invoices()
        #_logger.info("-> moves: " + str(moves))
        for move in moves:
            move.l10n_mx_edi_payment_method_id = self.partner_id.itl_payment_method_id.id
            move.l10n_mx_edi_usage = self.partner_id.itl_usage
            move.action_post()
        return moves