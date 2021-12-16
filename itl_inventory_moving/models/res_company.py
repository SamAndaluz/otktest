from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_transfer_approval = fields.Boolean(string="Transfer Approval", default=False, help="Enable new Transfer Approval flow using Approvals module.")
    itl_transfer_approval_category_id = fields.Many2one('approval.category', string="Approval category", help="Approval category to create when send transfer.")
    itl_location_dest_id = fields.Many2one('stock.location', "Destination Location")
    itl_location_id = fields.Many2one('stock.location', "Source Location")
    itl_logistic_product_id = fields.Many2one('product.product', string="Product for logistic company")