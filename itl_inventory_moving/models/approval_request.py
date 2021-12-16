from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    stock_picking_id = fields.Many2one('stock.picking', string="Transfer")
    warehouse_id = fields.Many2one(related="stock_picking_id.itl_warehouse_id", readonly=True)
    warehouse_dest_id = fields.Many2one(related="stock_picking_id.itl_warehouse_dest_id", readonly=True)
    
    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        
        if len(approvals) == len(self.mapped('approver_ids')) or len(approvals) == 0:
            if self.sudo().stock_picking_id:
                self.sudo().stock_picking_id.state = 'approved'
                self.sudo().stock_picking_id.state = 'assigned'
                if self.sudo().stock_picking_id.picking_type_id.code == 'internal':
                    if self.sudo().stock_picking_id.itl_source_contact_id and self.sudo().stock_picking_id.itl_source_contact_id.email:
                        self.sudo().stock_picking_id.send_shipping_email()
                if self.sudo().stock_picking_id.picking_type_id.code == 'outgoing':
                    if self.sudo().stock_picking_id.itl_origin_contact_id and self.sudo().stock_picking_id.itl_origin_contact_id.email:
                        self.sudo().stock_picking_id.send_shipping_email_sale()
                if self.sudo().stock_picking_id.picking_type_id.code in ['outgoing','internal'] and self.sudo().stock_picking_id.itl_delivery_by == 'logistic_company':
                    if self.sudo().stock_picking_id.itl_logistic_company_id and self.sudo().stock_picking_id.itl_logistic_company_id.email:
                        self.sudo().stock_picking_id.send_logistic_email()
                if self.sudo().stock_picking_id.picking_type_id.code in ['outgoing','internal'] and self.sudo().stock_picking_id.itl_delivery_by == 'employee':
                    if self.sudo().stock_picking_id.itl_employee_partner_id and self.sudo().stock_picking_id.itl_employee_partner_id.email:
                        self.sudo().stock_picking_id.send_employee_email()
                if self.sudo().stock_picking_id.itl_is_return:
                    if self.sudo().stock_picking_id.itl_origin_contact_id and self.sudo().stock_picking_id.itl_origin_contact_id.email:
                        self.sudo().stock_picking_id.send_receiving_return_email()
                    if self.sudo().stock_picking_id.itl_delivery_by == 'logistic_company':
                        if self.sudo().stock_picking_id.itl_logistic_company_id and self.sudo().stock_picking_id.itl_logistic_company_id.email:
                            self.sudo().stock_picking_id.send_logistic_email()
                    if self.sudo().stock_picking_id.itl_delivery_by == 'employee':
                        if self.sudo().stock_picking_id.itl_employee_partner_id and self.sudo().stock_picking_id.itl_employee_partner_id.email:
                            self.sudo().stock_picking_id.send_employee_email()
                
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        if self.sudo().stock_picking_id:
            self.sudo().stock_picking_id.state = 'to_approve'
            
    #Inherit method
    def action_cancel(self):
        if self.sudo().stock_picking_id:
            if self.sudo().stock_picking_id.state not in ['done','sale']:
                self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
                self.mapped('approver_ids').write({'status': 'cancel'})
            else:
                raise UserError(_('No se puede cancelar una Solicitud de Aprobación relacionada a una Orden de Venta en estatus "Pedido de venta" o "Bloqueado"'))
        else:
            super(ApprovalRequestCustom, self).action_cancel()
    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.sudo().stock_picking_id:
            view = self.env.ref('itl_approval_sale.send_message_feedback_form')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['stock_picking_id'] = self.sudo().stock_picking_id.id

            return {
                'name': 'Reason',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'send.message.feedback.stock.picking',
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
                if request.sudo().stock_picking_id and request.sudo().stock_picking_id.state == 'to_approve':
                    request.sudo().stock_picking_id.message_post_with_view('itl_inventory_moving.message_approval_transfer_origin_link',
                                                            values={'self': request.sudo().stock_picking_id, 'origin': request},
                                                            subtype_id=self.env.ref('mail.mt_note').id
                                                        )
                    
