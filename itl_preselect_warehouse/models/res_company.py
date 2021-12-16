from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'
    
    itl_user_warehouse_ids = fields.Many2many('itl.users.warehouse', 'itl_users_warehouse_rel', 'company_id')
    itl_user_warehouse_condition_ids = fields.Many2many('itl.users.warehouse.condition', 'itl_users_warehouse_condition_rel', 'company_id')
    
    
class ItlUsersWarehouse(models.Model):
    _name = 'itl.users.warehouse'
    
    itl_user_ids = fields.Many2many('res.users', string="Users")
    itl_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    
    
class ItlUsersWarehouseCondition(models.Model):
    _name = 'itl.users.warehouse.condition'
    
    itl_user_ids = fields.Many2many('res.users', string="Users")
    itl_warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    itl_condition = fields.Selection([('less_than','Menor igual'),('greater_than','Mayor igual')], string="Condition")
    itl_qty_condition = fields.Integer(string="Quantity")