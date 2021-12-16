from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_partner_approval = fields.Boolean(related="company_id.itl_partner_approval", string="Contact Approval New", default=False, help="Enable new Contact Approval flow using Approvals module.", readonly=False)
    itl_partner_approval_category_id = fields.Many2one(related="company_id.itl_partner_approval_category_id", string="Approval category", help="Approval category to create when send contact.", readonly=False)