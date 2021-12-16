from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_transfer_approval = fields.Boolean(related="company_id.itl_transfer_approval", string="Transfer Approval New", default=False, help="Enable new Transfer Approval flow using Approvals module.", readonly=False)
    itl_transfer_approval_category_id = fields.Many2one(related="company_id.itl_transfer_approval_category_id", string="Approval category", help="Approval category to create when send transfer.", readonly=False)
    itl_location_dest_id = fields.Many2one(related="company_id.itl_location_dest_id",string="Destination Location", readonly=False)
    itl_location_id = fields.Many2one(related="company_id.itl_location_id",string="Source Location", readonly=False)
    itl_logistic_product_id = fields.Many2one(related="company_id.itl_logistic_product_id", string="Product for logistic company", readonly=False)