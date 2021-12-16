from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    
    itl_journal_id = fields.Many2one('account.journal', string="Journal")
    itl_debit_account = fields.Many2one('account.account', string='Debit account')
    itl_credit_account = fields.Many2one('account.account', string='Credit account')