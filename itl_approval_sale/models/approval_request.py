from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    sale_id = fields.Many2one('sale.order', string="Sale Order related")
    sale_partner_id = fields.Many2one('res.partner', related="sale_id.partner_id", readonly=True)
    sale_currency_id = fields.Many2one(related="sale_id.currency_id", readonly=True)
    
    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        _logger.info("---> approvals: " + str(len(approvals)))
        
        if len(approvals) == len(self.mapped('approver_ids')) or len(approvals) == 0:
            if self.sale_id:
                self.sale_id.state = 'approved'
                self.sale_id.sudo().action_confirm()
    
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        if self.sale_id:
            self.sale_id.state = 'to_approve'
            
    #Inherit method
    def action_cancel(self):
        if self.sale_id:
            if self.sale_id.state not in ['done','sale']:
                self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
                self.mapped('approver_ids').write({'status': 'cancel'})
                self.sale_id.action_cancel()
                self.send_email_notification_done()
            else:
                raise UserError(_('No se puede cancelar una Solicitud de Aprobación relacionada a una Orden de Venta en estatus "Pedido de venta" o "Bloqueado"'))
        else:
            super(ApprovalRequestCustom, self).action_cancel()

    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.sale_id:
            view = self.env.ref('itl_approval_sale.send_message_feedback_form')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['sale_id'] = self.sale_id.id

            return {
                'name': 'Reason',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'send.message.feedback',
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
            # Una vez que está aprobada se manda una notificación al log del registro de la SO
            if request.request_status == 'approved':
                if request.sale_id and request.sale_id.state == 'to_approve':
                    request.sale_id.message_post_with_view('itl_approval_sale.message_approval_sale_origin_link',
                                                            values={'self': request.sale_id, 'origin': request},
                                                            subtype_id=self.env.ref('mail.mt_note').id
                                                        )
                    
