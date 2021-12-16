from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_so_approval = fields.Boolean(related="company_id.itl_so_approval", string="Sale Order Approval New", default=False, help="Enable new SO Approval flow using Approvals module.", readonly=False)
    itl_so_approval_category_id = fields.Many2one(related="company_id.itl_so_approval_category_id", string="Approval category", help="Approval category to create when send sale order.", readonly=False)