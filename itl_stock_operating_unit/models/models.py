from psycopg2 import OperationalError, Error

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    itl_loc_operating_unit_id = fields.Many2one('operating.unit', related='location_id.operating_unit_id')
    
    def action_view_quants(self):
        self = self.with_context(search_default_internal_loc=1)
        domain = []
        if self.user_has_groups('stock.group_production_lot,stock.group_stock_multi_locations'):
            # fixme: erase the following condition when it'll be possible to create a new record
            # from a empty grouped editable list without go through the form view.
            if self.search_count([
                ('company_id', '=', self.env.company.id),
                ('location_id.usage', 'in', ['internal', 'transit'])
            ]):
                self = self.with_context(
                    search_default_productgroup=1,
                    search_default_locationgroup=1
                )
        if not self.user_has_groups('stock.group_stock_multi_locations'):
            company_user = self.env.company
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
            if warehouse:
                self = self.with_context(default_location_id=warehouse.lot_stock_id.id)

        # If user have rights to write on quant, we set quants in inventory mode.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
        # ITL Customization
        if not self.user_has_groups('operating_unit.group_manager_operating_unit'):
            domain = [('itl_loc_operating_unit_id','in',self.env.user.operating_unit_ids.ids)]
        
        return self._get_quants_action(domain=domain, extend=True)
    