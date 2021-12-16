# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"
    
    approval_request = fields.Boolean(string="Approval request", default=False)
    sale_type_account = fields.Many2one('account.account')
    delivery_message = fields.Text()
    active = fields.Boolean(default=True)