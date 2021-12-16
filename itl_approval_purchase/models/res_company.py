from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    po_approval = fields.Boolean(string="Purchase Order Approval New", default=False, help="Enable new PO Approval flow using Approvals module.")
    po_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send purchase order.")