from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class ExpenseSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    approver_1_product = fields.Many2one('res.users', string="Approver 1", required=True)
    approver_2_product = fields.Many2one('res.users', string="Approver 2", required=True)
    activity_type_to_create_product = fields.Many2one('mail.activity.type', string="Activity type to create", required=True)
    note_product = fields.Text(string="Note")

    def set_values(self):
        res = super(ExpenseSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        approver_1_product = self.approver_1_product and self.approver_1_product.id or False
        approver_2_product = self.approver_2_product and self.approver_2_product.id or False
        activity_type_to_create_product = self.activity_type_to_create_product and self.activity_type_to_create_product.id or False
        note_product = self.note_product or False
        
        param.set_param('product_approval.approver_1_product', approver_1_product)
        param.set_param('product_approval.approver_2_product', approver_2_product)
        param.set_param('product_approval.activity_type_to_create_product', activity_type_to_create_product)
        param.set_param('product_approval.note_product', note_product)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(ExpenseSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        approver_1_product = ICPSudo.get_param('product_approval.approver_1_product')
        approver_2_product = ICPSudo.get_param('product_approval.approver_2_product')
        activity_type_to_create_product = ICPSudo.get_param('product_approval.activity_type_to_create_product')
        note_product = ICPSudo.get_param('product_approval.note_product')
        
        res.update(
            approver_1_product=int(approver_1_product),
            approver_2_product=int(approver_2_product),
            activity_type_to_create_product=int(activity_type_to_create_product),
            note_product=note_product
        )
        
        return res