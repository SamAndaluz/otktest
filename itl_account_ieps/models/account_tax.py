from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountTax(models.Model):
    _inherit = 'account.tax'
    
    itl_include_in_tax = fields.Boolean(string="Incluir en impuestos")
    itl_taxes = fields.Many2many('account.tax','itl_taxe_taxe','itl_tax_id','tax_id', string="Impuestos")
    itl_hide_in = fields.Boolean(string="Ocultar en ventas")
    