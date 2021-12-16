from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class ExpenseSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    approver_1 = fields.Many2one('res.users', string="Approver 1", required=True)
    approver_2 = fields.Many2one('res.users', string="Approver 2", required=True)
    activity_type_to_create = fields.Many2one('mail.activity.type', string="Activity type to create", required=True)
    note = fields.Text(string="Note")

    def set_values(self):
        res = super(ExpenseSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        approver_1 = self.approver_1 and self.approver_1.id or False
        approver_2 = self.approver_2 and self.approver_2.id or False
        activity_type_to_create = self.activity_type_to_create and self.activity_type_to_create.id or False
        note = self.note or False
        
        param.set_param('hr_expense_extended.approver_1', approver_1)
        param.set_param('hr_expense_extended.approver_2', approver_2)
        param.set_param('hr_expense_extended.activity_type_to_create', activity_type_to_create)
        param.set_param('hr_expense_extended.note', note)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(ExpenseSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        approver_1 = ICPSudo.get_param('hr_expense_extended.approver_1')
        approver_2 = ICPSudo.get_param('hr_expense_extended.approver_2')
        activity_type_to_create = ICPSudo.get_param('hr_expense_extended.activity_type_to_create')
        note = ICPSudo.get_param('hr_expense_extended.note')
        
        res.update(
            approver_1=int(approver_1),
            approver_2=int(approver_2),
            activity_type_to_create=int(activity_type_to_create),
            note=note
        )
        
        return res