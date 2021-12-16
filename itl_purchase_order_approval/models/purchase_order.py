# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

import logging
_logger = logging.getLogger(__name__)


class itl_purchase_order_approval(models.Model):
    _inherit = 'purchase.order'
    
    has_first_approval = fields.Boolean(string="Has first approval")
    
    @api.depends()
    def _get_finance_manager(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        finance_manager_purchase = ICPSudo.get_param('itl_purchase_order_approval.finance_manager_purchase')
        fm_purchase_user_id = self.env['res.users'].browse(int(finance_manager_purchase))
        user_id = self.env.user.id
        _logger.info("user_id: " + str(user_id) + " - fm_purchase_user_id: " + str(fm_purchase_user_id.id))
        if user_id == fm_purchase_user_id.id:
            self.is_finance_manager = True
        else:
            self.is_finance_manager = False
    
    is_finance_manager = fields.Boolean(compute="_get_finance_manager")
    
    def button_confirm(self):
        rec = super(itl_purchase_order_approval, self).button_confirm()
        
        self.send_activity()
        
        return rec
    
    def button_approve(self, force=False):
        rec = super(itl_purchase_order_approval, self).button_approve()
        
        self.mark_task_as_done()
    
    def button_approve_first(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_purchase = ICPSudo.get_param('itl_purchase_order_approval.activity_type_to_create_purchase') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_purchase))
        note_purchase = ICPSudo.get_param('itl_purchase_order_approval.note_purchase') or False
        
        approver_2_purchase = ICPSudo.get_param('itl_purchase_order_approval.approver_2_purchase')
        approver_2_purchase = self.env['res.users'].browse(int(approver_2_purchase))
        
        activity2 = False
        
        if not approver_2_purchase:
            raise UserError("There is not second approver configured")
        
        activity2 = self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'date_deadline': fields.Date.today(),
                'summary': activity_type.name,
                'user_id': approver_2_purchase.id,
                'note': note_purchase,
                'res_id': self.id,
                'res_model': self.env['ir.model']._get(self._name).name,
                'res_model_id': self.env['ir.model']._get(self._name).id,
            })
        activity2.action_close_dialog()
        
        self.mark_task_as_done()
        
        self.has_first_approval = True
    
    def send_activity(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_purchase = ICPSudo.get_param('itl_purchase_order_approval.activity_type_to_create_purchase') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_purchase))
        note_purchase = ICPSudo.get_param('itl_purchase_order_approval.note_purchase') or False
        finance_manager_purchase = ICPSudo.get_param('itl_purchase_order_approval.finance_manager_purchase')
        fm_purchase_user_id = self.env['res.users'].browse(int(finance_manager_purchase))

        activity1 = False
        user_id = self.env.user.id
        
        if not fm_purchase_user_id:
            raise UserError("There is not finance manager configured.")
        
        #if user_id == fm_purchase_user_id.id:
        #    raise UserError("Second approver must not be the same that current user.")

        activity1 = self.env['mail.activity'].create({
                'activity_type_id': activity_type.id,
                'date_deadline': fields.Date.today(),
                'summary': activity_type.name,
                'user_id': fm_purchase_user_id.id,
                'note': note_purchase,
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
            