# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"
    
    
    is_purchase_or_sale_origin = fields.Boolean(compute="_check_purchase_or_sale_order_origin", default=False)
    has_first_approval = fields.Boolean(string="Has first approval")
    is_finance_manager = fields.Boolean(compute="_get_finance_manager")
    is_approver2 = fields.Boolean(string="Is approver", compute="_check_approver2", store=False)
    was_send = fields.Boolean(string="Was send to approve")
    
    def action_post_itl_invoice_approval(self):
        self.action_post()
    
    def _check_approver2(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        approver_2_invoice = ICPSudo.get_param('itl_invoice_approval.approver_2_invoice')
        approver_2_invoice_user_id = self.env['res.users'].browse(int(approver_2_invoice))
        
        user_id = self.env.user.id

        if approver_2_invoice_user_id.id == user_id:
            self.is_approver2 = True
        else:
            self.is_approver2 = False
    
    @api.depends()
    def _check_purchase_or_sale_order_origin(self):
        if self.invoice_origin and 'P' in self.invoice_origin[0]:
            self.is_purchase_or_sale_origin = True
        elif self.journal_id and self.journal_id.type == 'sale':
            self.is_purchase_or_sale_origin = True
        else:
            purchase_id = self.line_ids.mapped('purchase_line_id.order_id')
            sale_id = self.line_ids.mapped('sale_line_ids.order_id')
            if purchase_id or sale_id:
                self.is_purchase_or_sale_origin = True
            else:
                self.is_purchase_or_sale_origin = False
            
    @api.depends()
    def _get_finance_manager(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        finance_manager_invoice = ICPSudo.get_param('itl_invoice_approval.finance_manager_invoice')
        fm_invoice_user_id = self.env['res.users'].browse(int(finance_manager_invoice))
        user_id = self.env.user.id
        #_logger.info("user_id: " + str(user_id) + " - fm_invoice_user_id: " + str(fm_invoice_user_id.id))
        if user_id == fm_invoice_user_id.id:
            self.is_finance_manager = True
        else:
            self.is_finance_manager = False

    def button_send_to_approve(self):
        self.was_send = True
        self.send_activity()

    
    def action_post(self, force=False):
        rec = super(AccountMove, self).action_post()
        
        self.mark_task_as_done()
    
    def button_approve_first(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_invoice = ICPSudo.get_param('itl_invoice_approval.activity_type_to_create_invoice') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_invoice))
        note_invoice = ICPSudo.get_param('itl_invoice_approval.note_invoice') or False
        
        approver_2_invoice = ICPSudo.get_param('itl_invoice_approval.approver_2_invoice')
        approver_2_invoice = self.env['res.users'].browse(int(approver_2_invoice))
        
        activity2 = False
        
        if not approver_2_invoice:
            raise UserError("There is not second approver configured")
        
        activity2 = self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'date_deadline': fields.Date.today(),
                'summary': activity_type.name,
                'user_id': approver_2_invoice.id,
                'note': note_invoice,
                'res_id': self.id,
                'res_model': self.env['ir.model']._get(self._name).name,
                'res_model_id': self.env['ir.model']._get(self._name).id,
            })
        activity2.action_close_dialog()
        
        self.mark_task_as_done()
        
        self.has_first_approval = True
    
    def send_activity(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_invoice = ICPSudo.get_param('itl_invoice_approval.activity_type_to_create_invoice') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_invoice))
        note_invoice = ICPSudo.get_param('itl_invoice_approval.note_invoice') or False
        finance_manager_invoice = ICPSudo.get_param('itl_invoice_approval.finance_manager_invoice')
        fm_invoice_user_id = self.env['res.users'].browse(int(finance_manager_invoice))

        activity1 = False
        user_id = self.env.user.id
        
        if not fm_invoice_user_id:
            raise UserError("There is not finance manager configured.")
        
        if user_id == fm_invoice_user_id.id:
            raise UserError("Second approver must not be the same that current user.")

        activity1 = self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'date_deadline': fields.Date.today(),
                'summary': activity_type.name,
                'user_id': fm_invoice_user_id.id,
                'note': note_invoice,
                'res_id': self.id,
                'res_model': self.env['ir.model']._get(self._name).name,
                'res_model_id': self.env['ir.model']._get(self._name).id,
            })
        activity1.action_close_dialog()
        
    
    def mark_task_as_done(self):
        user_id = self.env.user.id
        
        activity = self.env['mail.activity'].search([('user_id','=', user_id),('res_id','=',self.id),('res_model_id','=',self.env['ir.model']._get(self._name).id)])
        if activity:
            activity._action_done()