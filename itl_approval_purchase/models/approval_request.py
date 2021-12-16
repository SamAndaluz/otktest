from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    purchase_id = fields.Many2one('purchase.order', string="Purchace Order related")
    purchase_partner_id = fields.Many2one('res.partner', related="purchase_id.partner_id", readonly=True)
    purchase_currency_id = fields.Many2one('res.currency', related="purchase_id.currency_id", readonly=True)
    purchase_amount_total = fields.Monetary(related="purchase_id.amount_total", currency_field='purchase_currency_id', readonly=True)

    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self.sudo()).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        if len(approvals) == len(self.mapped('approver_ids')):
            if self.purchase_id:
                self.purchase_id.button_approve()
    
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        if self.purchase_id:
            self.purchase_id.state = 'to approve'
            
        
    #Inherit method
    def action_cancel(self):
        if self.purchase_id:
            if self.purchase_id.state not in ['done','purchase']:
                self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
                self.mapped('approver_ids').write({'status': 'cancel'})
                self.purchase_id.button_cancel()
                self.send_email_notification_done()
            else:
                raise UserError(_('No se puede cancelar una Solicitud de Aprobación relacionada a una Orden de Compra en estatus "Pedido de compra" o "Bloqueado"'))
        else:
            super(ApprovalRequestCustom, self).action_cancel()
    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.purchase_id and not self.bill_id:
            _logger.info("----<> action_refuse")
            view = self.env.ref('itl_approval_purchase.send_message_feedback_form_purchase')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['purchase_id'] = self.purchase_id.id
            return {
                'name': 'Reason',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'send.message.feedback.purchase',
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
                if request.purchase_id and request.purchase_id.state == 'to approve':
                    request.purchase_id.message_post_with_view('itl_approval_purchase.message_approval_origin_link',
                                                        values={'self': request.purchase_id, 'origin': request},
                                                        subtype_id=self.env.ref('mail.mt_note').id
                                                        )
