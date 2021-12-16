from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class HrExpenseCustom(models.Model):
    _inherit = "hr.expense.sheet"
    
    
    itl_approval_date = fields.Date(string="Approval Date", compute="_get_approval_detail")
    itl_proven_amount = fields.Monetary(string="Proven Amount", currency_field='currency_id', compute="_get_clearing_details")
    itl_balance_amount = fields.Monetary(string="Balance", currency_field='currency_id', compute="_get_balance")
    itl_last_invoice_date = fields.Date(string="Last Invoice Date", compute="_get_clearing_details")
    
    itl_mngr_appr_date = fields.Date(string="Apprv Manager Date", compute="_get_approval_detail")
    itl_finance_1_appr_date = fields.Date(string="Apprv Fin 1 Date", compute="_get_approval_detail")
    itl_finance_2_appr_date = fields.Date(string="Apprv Fin 2 Date", compute="_get_approval_detail")
    itl_payment_date = fields.Date(string="Payment date", compute="_get_payment_details")
    
    itl_clearing_report_ids = fields.Many2many("hr.expense.sheet", compute="_get_clearing_details")
    
    
    # Inherit
    def read(self, fields=None, load='_classic_read'):
        self = self.sudo()
        rec = super(HrExpenseCustom, self).read(fields, load)
        
        return rec
    
    def _get_approval_detail(self):
        for exp_sheet in self:
            exp_sheet.itl_mngr_appr_date = False
            exp_sheet.itl_finance_1_appr_date = False
            exp_sheet.itl_finance_2_appr_date = False
            exp_sheet.itl_approval_date = False
            if exp_sheet.approval_request_id and len(exp_sheet.approval_request_id.approver_ids) > 0:
                approval_request_id = exp_sheet.approval_request_id
                if approval_request_id.approver_ids[0].status == 'approved':
                    exp_sheet.itl_mngr_appr_date = approval_request_id.approver_ids[0].write_date
                if len(approval_request_id.approver_ids) > 1 and approval_request_id.approver_ids[1].status == 'approved':
                    exp_sheet.itl_finance_1_appr_date = approval_request_id.approver_ids[1].write_date
                if len(approval_request_id.approver_ids) > 2 and approval_request_id.approver_ids[2].status == 'approved':
                    exp_sheet.itl_finance_2_appr_date = approval_request_id.approver_ids[2].write_date
                
                if approval_request_id.approver_ids[-1].status == 'approved':
                    exp_sheet.itl_approval_date = approval_request_id.approver_ids[-1].write_date
                    
    def _get_clearing_details(self):
        for exp_sheet in self:
            exp_sheet.itl_clearing_report_ids = False
            exp_sheet.itl_proven_amount = False
            exp_sheet.itl_last_invoice_date = False
            clearing_exp_sheet_ids = self.env['hr.expense.sheet'].search([('advance_sheet_id','=',exp_sheet.id)])
            exp_sheet.itl_proven_amount = exp_sheet.total_amount - exp_sheet.clearing_residual
            if len(clearing_exp_sheet_ids) > 0:
                clearing_exp_sheet_approved_ids = clearing_exp_sheet_ids.filtered(lambda i: i.state == 'done')
                if len(clearing_exp_sheet_approved_ids) > 0:
                    #itl_proven_amount = sum(clearing_exp_sheet_approved_ids.mapped('total_amount'))
                    #exp_sheet.itl_proven_amount = itl_proven_amount

                    last_clearing_id = clearing_exp_sheet_approved_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    exp_sheet.itl_last_invoice_date = last_clearing_id.create_date

                exp_sheet.itl_clearing_report_ids = [(6, 0, clearing_exp_sheet_ids.ids)]
                
    def _get_balance(self):
        for exp_sheet in self:
            exp_sheet.itl_balance_amount = exp_sheet.total_amount - exp_sheet.itl_proven_amount
            
    def _get_payment_details(self):
        for exp_sheet in self:
            exp_sheet.itl_payment_date = False
            if exp_sheet.state == 'done' and exp_sheet.account_move_id:
                
                if exp_sheet.payment_mode == 'company_account':
                    payment_ids = exp_sheet.account_move_id.line_ids.mapped('payment_id')
                    if len(payment_ids) > 0:
                        exp_sheet.itl_payment_date = payment_ids[0].payment_date
                else:
                    reconcile_line_ids = exp_sheet.account_move_id.line_ids._reconciled_lines()
                    aml = self.env['account.move.line'].browse(reconcile_line_ids)
                    payment_ids = aml.mapped('payment_id')
                    if len(payment_ids) > 0:
                        exp_sheet.itl_payment_date = payment_ids[0].payment_date
                        
                