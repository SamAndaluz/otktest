from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string="Expense sheet")
    exs_employee_id = fields.Many2one('hr.employee', related="expense_sheet_id.employee_id", readonly=True)

    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        if len(approvals) == len(self.mapped('approver_ids')):
            if self.sudo().expense_sheet_id:
                self.sudo().expense_sheet_id.approve_expense_sheets()
                self.sudo().expense_sheet_id.action_sheet_move_create()
                #if not self.sudo().expense_sheet_id.account_move_id:
                #    self.sudo().expense_sheet_id.set_to_paid()
                #raise UserError("Testing...")
                #if self.sudo().expense_sheet_id.itl_advance_origin:
                #    self.sudo().expense_sheet_id.set_to_paid()
    
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        if self.expense_sheet_id:
            self.expense_sheet_id.state = 'submit'
            
        
    #Inherit method
    def action_cancel(self):
        if self.expense_sheet_id:
            self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
            self.mapped('approver_ids').write({'status': 'cancel'})
        else:
            super(ApprovalRequestCustom, self).action_cancel()
    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.expense_sheet_id:
            _logger.info("----<> action_refuse")
            view = self.env.ref('itl_approval_expenses.send_message_feedback_form_expenses')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['expense_sheet_id'] = self.expense_sheet_id.id
            return {
                'name': 'Reason',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'send.message.feedback.expenses',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            return super(ApprovalRequestCustom, self).action_refuse()
        
    # Inherit method
    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        rec = super(ApprovalRequestCustom, self)._compute_request_status()
        for request in self:
            # Una vez que está aprobada se manda una notificación al log del registro de la PO
            if request.request_status == 'approved':
                if request.expense_sheet_id and request.expense_sheet_id.state == 'approve':
                    request.purchase_id.message_post_with_view('itl_approval_expenses.message_approval_expense_origin_link',
                                                        values={'self': request.expense_sheet_id, 'origin': request},
                                                        subtype_id=self.env.ref('mail.mt_note').id
                                                        )
