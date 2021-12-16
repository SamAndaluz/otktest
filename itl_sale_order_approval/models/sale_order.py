# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class itl_sale_order_approval(models.Model):
    _inherit = 'sale.order'
    
    def _check_approver(self):
        user_id = self.env.user.id
        activity = self.env['mail.activity'].search([('user_id','=', user_id),('res_id','=',self.id),('res_model_id','=',self.env['ir.model']._get(self._name).id)])
        if activity:
            self.is_approver = True
        else:
            self.is_approver = False

    def _check_manager(self):
        user_id = self.env.user.id
        self._cr.execute("select distinct h2.id from hr_employee h1, hr_employee h2 where h1.parent_id = h2.id;")
        data = self._cr.dictfetchall()
        manager_ids = [d['id'] for d in data]
        manager_ids = self.env['hr.employee'].browse(manager_ids).mapped('user_id').ids
            
        if user_id in manager_ids:
            self.is_manager = True
        else:
            self.is_manager = False

    #is_record_creator = fields.Boolean('Is record creator', compute="_get_record_creator", store=False)
    approval_request = fields.Boolean(related='type_id.approval_request', string="Approval request", readonly=True)
    is_approver = fields.Boolean(string="Is approver", compute="_check_approver", store=False)
    is_manager = fields.Boolean(string="Is employee manager", compute="_check_manager", store=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to_approve', 'To approve'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def send_to_approve(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_sale = ICPSudo.get_param('itl_sale_order_approval.activity_type_to_create_sale') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_sale))
        note_sale = ICPSudo.get_param('itl_sale_order_approval.note_sale') or False
        
        if self.type_id.approval_request:
            employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            user_manager_id = False
            if employee_id.parent_id and employee_id.parent_id.user_id:
                user_manager_id = employee_id.parent_id.user_id.id
            if user_manager_id:
                activity = self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'date_deadline': fields.Date.today(),
                    'summary': activity_type.name,
                    'user_id': user_manager_id,
                    'note': note_sale,
                    'res_id': self.id,
                    'res_model': self.env['ir.model']._get(self._name).name,
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                })
                activity.action_close_dialog()
                self.state = 'to_approve'
    
    def action_confirm(self):
        record = super(itl_sale_order_approval, self).action_confirm()
        user_id = self.env.user.id
        activity = self.env['mail.activity'].search([('user_id','=', user_id),('res_id','=',self.id),('res_model_id','=',self.env['ir.model']._get(self._name).id)])
        if activity:
            activity._action_done()
            
            
    """
    @api.model
    def create(self, vals):
        record = super(itl_sale_order_approval, self).create(vals)
        
        ICPSudo = self.env['ir.config_parameter'].sudo()
        activity_type_to_create_sale = ICPSudo.get_param('itl_sale_order_approval.activity_type_to_create_sale') or False
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_sale))
        note_sale = ICPSudo.get_param('itl_sale_order_approval.note_sale') or False
        
        if record.type_id.approval_request:
            employee_id = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            user_manager_id = False
            if employee_id.parent_id and employee_id.parent_id.user_id:
                user_manager_id = employee_id.parent_id.user_id.id
            if user_manager_id:
                activity = self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'date_deadline': fields.Date.today(),
                    'summary': activity_type.name,
                    'user_id': user_manager_id,
                    'note': note_sale,
                    'res_id': record.id,
                    'res_model': self.env['ir.model']._get(self._name).name,
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                })
                activity.action_close_dialog()
        
        return record
    """