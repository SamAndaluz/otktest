# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplateCustom(models.Model):
    _inherit = "product.template"
    
    
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the product without removing it.",
        tracking=False)
    
    approve = fields.Boolean('Approved', default=False, tracking=True)
    
    current_user = fields.Many2one('res.users', compute='_get_current_user')

    @api.depends()
    def _get_current_user(self):
        for rec in self:
            rec.current_user = self.env.user
    
    
    @api.model_create_multi
    def create(self, vals_list):
        record = super(ProductTemplateCustom, self).create(vals_list)
        
        self.set_activity(record)
        
        return record
    
    def set_activity(self, record):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        approver_1_product = ICPSudo.get_param('product_approval.approver_1_product') or False
        approver_2_product = ICPSudo.get_param('product_approval.approver_2_product') or False
        activity_type_to_create_product = ICPSudo.get_param('product_approval.activity_type_to_create_product') or False
        note_product = ICPSudo.get_param('product_approval.note_product') or False
        
        user_approver_1 = self.env['res.users'].browse(int(approver_1_product))
        user_approver_2 = self.env['res.users'].browse(int(approver_2_product))
        activity_type = self.env['mail.activity.type'].browse(int(activity_type_to_create_product))
        
        if not approver_1_product:
            raise UserError("There is not Approver 1 configured.")
        if not approver_2_product:
            raise UserError("There is not Approver 2 configured.")
        if not activity_type_to_create_product:
            raise UserError("There is not Activity type configured.")

        activity1 = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'date_deadline': fields.Date.today(),
            'summary': activity_type.name,
            'user_id': user_approver_1.id,
            'note': note_product,
            'res_id': record.id,
            'res_model': self.env['ir.model']._get(self._name).name,
            'res_model_id': self.env['ir.model']._get(self._name).id,
        })
        
        activity2 = self.env['mail.activity'].create({
            'activity_type_id': activity_type.id,
            'date_deadline': fields.Date.today(),
            'summary': activity_type.name,
            'user_id': user_approver_2.id,
            'note': note_product,
            'res_id': record.id,
            'res_model': self.env['ir.model']._get(self._name).name,
            'res_model_id': self.env['ir.model']._get(self._name).id,
        })
        
        activity1.action_close_dialog()
        activity2.action_close_dialog()
    
    def approve_product(self):
        self.approve = True
        
        user_id = self.env.user.id
        
        activity = self.env['mail.activity'].search([('user_id','=', user_id),('res_id','=',self.id),('res_model_id','=',self.env['ir.model']._get(self._name).id)])
        
        if activity:
            activity._action_done()