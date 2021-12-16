# -*- coding: utf-8 -*-

from odoo import models, fields, api


class itl_sale_channel(models.Model):
    _name = 'sale.channel'
    _description = "Sale Channel"
    
    name = fields.Char(string="Channel name", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic account", required=True)
    price_list_id = fields.Many2one('product.pricelist', string="Pricelist", required=True)
