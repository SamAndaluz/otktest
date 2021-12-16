from odoo import fields, models, tools

class UsersImplied(models.Model):
    _inherit = 'res.users'
    
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=10)