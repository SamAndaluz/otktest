from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_vendor_payment_approval = fields.Boolean(related="company_id.itl_vendor_payment_approval", string="Vendor bill payment Approval", default=False, help="Enable new Vendor bill payment flow using Approvals module.", readonly=False)
    itl_vendor_payment_approval_category_id = fields.Many2one(related="company_id.itl_vendor_payment_approval_category_id", string="Approval category", 
                                                           help="Approval category to create when send vendor bill payment approval request.", readonly=False)
    itl_job_ids = fields.Many2many('hr.job', related='company_id.itl_job_ids', readonly=False)