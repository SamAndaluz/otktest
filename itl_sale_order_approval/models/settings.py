from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class SaleSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    activity_type_to_create_sale = fields.Many2one('mail.activity.type', string="Activity type to create", required=True)
    note_sale = fields.Text(string="Note")

    def set_values(self):
        res = super(SaleSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_sale = self.activity_type_to_create_sale and self.activity_type_to_create_sale.id or False
        note_sale = self.note_sale or False
        
        param.set_param('itl_sale_order_approval.activity_type_to_create_sale', activity_type_to_create_sale)
        param.set_param('itl_sale_order_approval.note_sale', note_sale)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(SaleSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_sale = ICPSudo.get_param('itl_sale_order_approval.activity_type_to_create_sale')
        note_sale = ICPSudo.get_param('itl_sale_order_approval.note_sale')
        
        res.update(
            activity_type_to_create_sale=int(activity_type_to_create_sale),
            note_sale=note_sale
        )
        
        return res