from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    po_approval = fields.Boolean(related="company_id.po_approval", 
                                 string="Purchase Order Approval New", 
                                 default=False, 
                                 help="Enable new PO Approval flow using Approvals module.",
                                readonly=False)
    po_approval_category_id = fields.Many2one(related="company_id.po_approval_category_id", string="Approval category", help="Approval category to create when send purchase order.", readonly=False)