from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_pricelist_approval = fields.Boolean(related="company_id.itl_pricelist_approval", string="Pricelist Approval New", default=False, help="Enable new Pricelist Approval flow using Approvals module.", readonly=False)
    itl_pricelist_approval_category_id = fields.Many2one(related="company_id.itl_pricelist_approval_category_id", string="Approval category", help="Approval category to create when send pricelist.", readonly=False)