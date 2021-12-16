from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_journal_id = fields.Many2one(related="company_id.itl_journal_id", string="Journal", default=False, help="Journal para póliza de recepción temporal.", readonly=False)
    itl_debit_account = fields.Many2one(related="company_id.itl_debit_account", string="Debit account", help="Cuenta contable de débito.", readonly=False)
    itl_credit_account = fields.Many2one(related="company_id.itl_credit_account", string="Credit account", help="Cuenta contable de crédito.", readonly=False)