from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    itl_can_change_type = fields.Boolean(compute="_check_can_change_type")
    
    
    def _check_can_change_type(self):
        self.itl_can_change_type = False
        if self.env.user.has_group('itl_sale_order_type.group_can_change_so_type'):
            self.itl_can_change_type = True