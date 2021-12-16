from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_partner_approval = fields.Boolean(string="Contact Approval", default=False, help="Enable new Contact Approval flow using Approvals module.")
    itl_partner_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send contact.")