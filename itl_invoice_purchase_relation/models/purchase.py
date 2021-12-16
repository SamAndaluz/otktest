# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class PurchaseInovice(models.Model):
    _inherit = 'purchase.order'
    
    invoice_related_id = fields.Many2one('account.move', string="Related bill")
    invoice_date = fields.Date(related="invoice_related_id.invoice_date", string="Bill date", readonly=True)
    invoice_amount_total = fields.Monetary(related="invoice_related_id.amount_total", string="Bill amount total", readonly=True)