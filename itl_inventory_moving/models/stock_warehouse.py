
from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    itl_encargado = fields.Many2one(
        'res.partner', string='Encargado de almacén', required=False,
        # only partners with internal users related.
        domain="['&', ('user_ids', '!=', False), ('user_ids.share', '=', False)]"
    )

    def write(self, values):
        warehouse = super(StockWarehouse, self).write(values)
        self.update_owner_group()
        return warehouse

    def update_owner_group(self):
        owner_group = self.env.ref('itl_stock_adjustment.group_warehouse_owners')
        relation_info = [(5, 0, 0)]  # at first we remove all users
        warehouses = self.env['stock.warehouse'].search([("itl_encargado", "!=", False)])
        for w in warehouses:
            user = self.env['res.users'].search([('partner_id', '=', w.itl_encargado.id)])
            if user:
                relation_info.append((4, user.id, 0))  # add actual owners

        owner_group.sudo().write({"users": relation_info})

