from odoo import api, fields, models, _
from odoo.exceptions import UserError
    
import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    bill_id = fields.Many2one('account.move', string="Bill related")
    bill_partner_id = fields.Many2one('res.partner', related="bill_id.partner_id", readonly=True)
    bill_currency_id = fields.Many2one('res.currency', related="bill_id.currency_id", readonly=True)
    bill_amount_total = fields.Monetary(related="bill_id.amount_total", currency_field='bill_currency_id', readonly=True)
    payment_purchase_id = fields.Many2one('purchase.order', string="Payment Purchace Order related")
    payment_purchase_partner_id = fields.Many2one('res.partner', related="payment_purchase_id.partner_id", readonly=True)
    payment_purchase_currency_id = fields.Many2one('res.currency', related="payment_purchase_id.currency_id", readonly=True)
    payment_purchase_amount_total = fields.Monetary(related="payment_purchase_id.amount_total", currency_field='purchase_currency_id', readonly=True)
    
    bill_ids = fields.Many2many('account.move', string='Bills', copy=False, store=True)
    is_first_approver = fields.Boolean(compute='_check_is_first_approver')
    
    itl_urgent_payment = fields.Boolean(related='payment_purchase_id.itl_urgent_payment', string="Urgent payment")
    itl_payment_date = fields.Date(related='payment_purchase_id.itl_payment_date', string="Payment date")
    itl_urgency_reason = fields.Text(related='payment_purchase_id.itl_urgency_reason', string="Reason of urgent payment")
    
    def _check_is_first_approver(self):
        self.is_first_approver = False
        if self.category_id.code == 'PAYMENT':
            employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
            if employee_id:
                if employee_id.job_id.id in self.env.company.itl_job_ids.ids:
                    self.is_first_approver = True
    
    #Inherit method
    def action_confirm(self):
        if self.itl_urgent_payment:
            self = self.with_context(not_send_email=True)
        super(ApprovalRequestCustom, self).action_confirm()
        
        if self.itl_urgent_payment:
            if self.next_approver_id:
                self.send_approval_email_notification_urgent()

    #Inherit method
    def action_approve(self, approver=None):
        _logger.info("=====> self._context: " + str(self._context))
        if self.itl_urgent_payment:
            self = self.with_context(not_send_email=True)
        rec = super(ApprovalRequestCustom, self).action_approve()
        
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        if self.itl_urgent_payment and self.next_approver_id and len(approvals) != len(self.mapped('approver_ids')):
            self.send_approval_email_notification_urgent()
        
        if self.category_id.code == 'PAYMENT':
            if not self._context.get('payment_wo_invoice') and self.is_first_approver and len(self.bill_ids) == 0:
                raise UserError("Debe seleccionar almenos una factura.")
            else:
                self.link_bill()
        if len(approvals) == len(self.mapped('approver_ids')) and not self._context.get('payment_wo_invoice'):
            if self.category_id.code == 'PAYMENT':
                if len(self.bill_ids) != 0:
                    for inv in self.bill_ids:
                        if inv.state == 'draft':
                            inv.action_post()
                #Se removió para que puedan aprobar las solicitudes antiguas
                else:
                    raise UserError("Debe seleccionar almenos una factura.")  
                    
    def send_approval_email_notification_urgent(self):
        template_id = self.env.ref('itl_approval_vendor_bill.itl_approval_email_notification_urgent', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        email_values = {'base_url': base_url}
        if template_id:
            self.env['mail.template'].browse(template_id.id).with_context(email_values).with_user(1).send_mail(self.id, force_send=True)
    
    # Inherit method
    def action_withdraw(self, approver=None):
        super(ApprovalRequestCustom,self).action_withdraw()
        #if self.sale_id:
        #    self.sale_id.state = 'to_approve'
            
    #Inherit method
    def action_cancel(self):
        if len(self.bill_ids) > 0:
            #for inv in self.bill_ids:
            #    inv.unlink_bill()
            #if self.bill_id.state not in ['posted']:
            self.sudo()._get_user_approval_activities(user=self.env.user).unlink()
            self.mapped('approver_ids').write({'status': 'cancel'})
            #else:
            #    raise UserError(_('No se puede cancelar una Solicitud de Aprobación relacionada a una factura en estatus "Posted"'))
        else:
            super(ApprovalRequestCustom, self).action_cancel()
    
    #Inherit method
    def action_refuse(self, approver=None):
        if self.payment_purchase_id:
            view = self.env.ref('itl_approval_vendor_bill.send_message_feedback_form_payment')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['purchase_id'] = self.payment_purchase_id.id
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
    """
    # Inherit method
    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        rec = super(ApprovalRequestCustom, self)._compute_request_status()
        for request in self:
            pass
            # Una vez que está aprobada se manda una notificación al log del registro de la SO
            #if request.request_status == 'approved':
            #    if request.sale_id and request.sale_id.state == 'to_approve':
            #        request.sale_id.message_post_with_view('itl_approval_sale.message_approval_sale_origin_link',
            #                                                values={'self': request.sale_id, 'origin': request},
            #                                                subtype_id=self.env.ref('mail.mt_note').id
            #                                            )
        _logger.info("######-> ITL_APPROVAL_VENDOR_BILL request_status: " + str(request.request_status))
    """
                    
    def link_bill(self):
        for inv in self.bill_ids:
            invoice_lines = []
            for inv_line in inv.invoice_line_ids:
                invoice_lines.append((4, inv_line.id))
            self.payment_purchase_id.order_line.invoice_lines = invoice_lines
            self.payment_purchase_id.invoice_ids = [(4, inv.id)]
            if inv.invoice_origin:
                lst_origin = str(inv.invoice_origin).split(',')
                if self.payment_purchase_id.name not in lst_origin:
                    inv.invoice_origin = inv.invoice_origin + ',' + self.payment_purchase_id.name
            else:
                inv.invoice_origin = self.payment_purchase_id.name
            inv.approval_request_vendor_bill_id = self.id
    
    """
    def unlink_bill(self):
        if self.bill_id:
            invoice_lines = []
            for inv_line in self.bill_id.invoice_line_ids:
                invoice_lines.append((3, inv_line.id))
            self.payment_purchase_id.order_line.invoice_lines = invoice_lines
            self.payment_purchase_id.invoice_ids = [(3, self.id)]
            if self.bill_id.invoice_origin:
                lst_origin = str(self.bill_id.invoice_origin).split(',')
                lst_origin.remove(self.payment_purchase_id.name)
                lst_origin.sort(reverse=False)
                origin = ",".join(lst_origin)
                self.bill_id.invoice_origin = origin

            #self.approval_request_vendor_bill_id.action_cancel()
    """
