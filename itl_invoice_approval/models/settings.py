from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class InvoiceSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    activity_type_to_create_invoice = fields.Many2one('mail.activity.type', string="Activity type to create", required=True)
    note_invoice = fields.Text(string="Note")
    finance_manager_invoice = fields.Many2one('res.users', string="Finance Manager", required=True)
    approver_2_invoice = fields.Many2one('res.users', string="Second approver", required=True)

    def set_values(self):
        res = super(InvoiceSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_invoice = self.activity_type_to_create_invoice and self.activity_type_to_create_invoice.id or False
        note_invoice = self.note_invoice or False
        finance_manager_invoice = self.finance_manager_invoice and self.finance_manager_invoice.id or False
        approver_2_invoice = self.approver_2_invoice and self.approver_2_invoice.id or False
        
        param.set_param('itl_invoice_approval.activity_type_to_create_invoice', activity_type_to_create_invoice)
        param.set_param('itl_invoice_approval.note_invoice', note_invoice)
        param.set_param('itl_invoice_approval.finance_manager_invoice', finance_manager_invoice)
        param.set_param('itl_invoice_approval.approver_2_invoice', approver_2_invoice)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(InvoiceSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        activity_type_to_create_invoice = ICPSudo.get_param('itl_invoice_approval.activity_type_to_create_invoice')
        note_invoice = ICPSudo.get_param('itl_invoice_approval.note_invoice')
        finance_manager_invoice = ICPSudo.get_param('itl_invoice_approval.finance_manager_invoice')
        approver_2_invoice = ICPSudo.get_param('itl_invoice_approval.approver_2_invoice')
        
        res.update(
            activity_type_to_create_invoice=int(activity_type_to_create_invoice),
            note_invoice=note_invoice,
            finance_manager_invoice=int(finance_manager_invoice),
            approver_2_invoice=int(approver_2_invoice)
        )
        
        return res