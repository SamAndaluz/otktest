
from odoo import fields, models, tools

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    
    
    code = fields.Char(string="Code")
    approval_hierarchy = fields.Boolean(string="Jerarquía de aprobación", default=False)
    #approver_ids = fields.One2many('res.users', 'approval_category_id', string="Aprobadores")
    