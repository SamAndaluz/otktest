from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        if len(approvals) == len(self.mapped('approver_ids')):
            if self.partner_id:
                self.sudo().partner_id.state = 'approved'
    
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        if self.partner_id:
            self.sudo().partner_id.state = 'to_approve'
            
        
    #Inherit method
    def action_cancel(self):
        if self.partner_id:
            _logger.info("---> partner action_cancel")
            self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
            self.mapped('approver_ids').write({'status': 'cancel'})
            self.sudo().partner_id.state = 'cancel'
            self.send_email_notification_done()
        else:
            super(ApprovalRequestCustom, self).action_cancel()
    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.partner_id:
            view = self.env.ref('itl_approval_contact.send_message_feedback_form_partner')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['partner_id'] = self.partner_id.id
            return {
                'name': 'Reason',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'send.message.feedback.partner',
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
                if request.partner_id and request.partner_id.state == 'to_approve':
                    request.purchase_id.message_post_with_view('itl_approval_contact.message_approval_contact_origin_link',
                                                        values={'self': request.purchase_id, 'origin': request},
                                                        subtype_id=self.env.ref('mail.mt_note').id
                                                        )