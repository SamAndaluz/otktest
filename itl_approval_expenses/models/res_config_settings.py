from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_expense_approval = fields.Boolean(related="company_id.itl_expense_approval", string="Expense Approval", default=False, help="Enable new Expense Approval flow using Approvals module.", readonly=False)
    itl_expense_approval_category_id = fields.Many2one(related="company_id.itl_expense_approval_category_id", string="Approval category", help="Approval category to create when send expense.", readonly=False)
    
    itl_account_anticipo_id = fields.Many2one(related="company_id.itl_account_anticipo_id", readonly=False)
    itl_account_cuentas_pagar_id = fields.Many2one(related="company_id.itl_account_cuentas_pagar_id", readonly=False)
    itl_account_iva_pend_id = fields.Many2one(related="company_id.itl_account_iva_pend_id", readonly=False)
    itl_account_iva_pag_id = fields.Many2one(related="company_id.itl_account_iva_pag_id", readonly=False)
    itl_special_expense_journal_id = fields.Many2one(related="company_id.itl_special_expense_journal_id", readonly=False)