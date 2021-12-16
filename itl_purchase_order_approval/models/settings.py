from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class PurchaseSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    activity_type_to_create_purchase = fields.Many2one('mail.activity.type', string="Activity type to create", required=True)
    note_purchase = fields.Text(string="Note")
    finance_manager_purchase = fields.Many2one('res.users', string="Finance Manager", required=True)
    approver_2_purchase = fields.Many2one('res.users', string="Second approver", required=True)

    def set_values(self):
        res = super(PurchaseSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_purchase = self.activity_type_to_create_purchase and self.activity_type_to_create_purchase.id or False
        note_purchase = self.note_purchase or False
        finance_manager_purchase = self.finance_manager_purchase and self.finance_manager_purchase.id or False
        approver_2_purchase = self.approver_2_purchase and self.approver_2_purchase.id or False
        
        param.set_param('itl_purchase_order_approval.activity_type_to_create_purchase', activity_type_to_create_purchase)
        param.set_param('itl_purchase_order_approval.note_purchase', note_purchase)
        param.set_param('itl_purchase_order_approval.finance_manager_purchase', finance_manager_purchase)
        param.set_param('itl_purchase_order_approval.approver_2_purchase', approver_2_purchase)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(PurchaseSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_purchase = ICPSudo.get_param('itl_purchase_order_approval.activity_type_to_create_purchase')
        note_purchase = ICPSudo.get_param('itl_purchase_order_approval.note_purchase')
        finance_manager_purchase = ICPSudo.get_param('itl_purchase_order_approval.finance_manager_purchase')
        approver_2_purchase = ICPSudo.get_param('itl_purchase_order_approval.approver_2_purchase')
        
        res.update(
            activity_type_to_create_purchase=int(activity_type_to_create_purchase),
            note_purchase=note_purchase,
            finance_manager_purchase=int(finance_manager_purchase),
            approver_2_purchase=int(approver_2_purchase)
        )
        
        return res