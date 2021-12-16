from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    itl_user_warehouse_ids = fields.Many2many(related="company_id.itl_user_warehouse_ids", string="User and Warehouse", readonly=False)
    itl_user_warehouse_condition_ids = fields.Many2many(related="company_id.itl_user_warehouse_condition_ids", string="User, Warehouse and conditions", readonly=False)