from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_expense_approval = fields.Boolean(string="Expense Approval", default=False, help="Enable new Expense Approval flow using Approvals module.")
    itl_expense_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send expense.")
    
    itl_account_anticipo_id = fields.Many2one('account.account')
    itl_account_cuentas_pagar_id = fields.Many2one('account.account')
    itl_account_iva_pend_id = fields.Many2one('account.account')
    itl_account_iva_pag_id = fields.Many2one('account.account')
    itl_special_expense_journal_id = fields.Many2one('account.journal')