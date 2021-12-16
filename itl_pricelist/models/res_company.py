from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_pricelist_approval = fields.Boolean(string="Pricelist Approval", default=False, help="Enable new Pricelist Approval flow using Approvals module.")
    itl_pricelist_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send pricelist.")