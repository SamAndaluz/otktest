# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccountSubtype(models.Model):
    _name = "account.account.subtype"
    _description = "Account Subtype"

    name = fields.Char(string='Account Subtype', required=True, translate=True)
    itl_include_initial_balance = fields.Boolean(string="Bring Accounts Balance Forward", help="Used in reports to know if we should consider journal items from the beginning of time instead of from the fiscal year only.")
    itl_type = fields.Selection([
        ('other', 'Regular'),
        ('receivable', 'Receivable'),
        ('payable', 'Payable'),
        ('liquidity', 'Liquidity'),
    ], required=True, default='other',
        help="The 'Subtype' is used for features available on "\
        "different types of accounts: liquidity type is for cash or bank accounts"\
        ", payable/receivable is for vendor/customer accounts.")
    itl_internal_group = fields.Selection([
        ('equity', 'Equity'),
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('off_balance', 'Off Balance'),
    ], string="Internal Group",
        required=True,
        help="The 'Internal Group' is used to filter accounts based on the internal group set on the account subtype.")
    itl_note = fields.Text(string='Description')
    
    
class AccountAccount(models.Model):
    _inherit = "account.account"
    
    user_subtype_id = fields.Many2one('account.account.subtype', string='Subtype',
        help="Account Subtype is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries.")
    itl_user_type_id = fields.Integer(related='user_type_id.id', string='Type ID')
    itl_user_subtype_id = fields.Integer(related='user_subtype_id.id', string='Subtype ID')
