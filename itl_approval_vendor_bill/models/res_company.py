from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_vendor_payment_approval = fields.Boolean(string="Vendor bill payment Approval", default=False, help="Enable new Vendor bill payment flow using Approvals module.")
    itl_vendor_payment_approval_category_id = fields.Many2one('approval.category', string="Approval category", 
                                                           help="Approval category to create when send vendor bill payment approval request.")
    itl_job_ids = fields.Many2many('hr.job')