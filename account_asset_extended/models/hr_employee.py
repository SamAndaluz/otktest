from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError


class HrEmployeePrivateCustom(models.Model):
    _inherit = "hr.employee"
    
    asset_ids = fields.One2many('account.asset', 'employee_id', string="Assets")