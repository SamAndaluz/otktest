# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    active = fields.Boolean(default=True)
    

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    active = fields.Boolean(default=True)
    

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    active = fields.Boolean(default=True)