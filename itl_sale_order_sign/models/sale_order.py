from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    type_delivery_message = fields.Text(related='type_id.delivery_message')
    
    # Inherit
    def _compute_access_url(self):
        
        _logger.info("---> _compute_access_url context: " + str(self._context))
        if self._context.get('only_sign'):
            for order in self:
                order.access_url = '/my/orders_sign/%s' % (order.id)
        else:
            super(SaleOrder, self)._compute_access_url()
            for order in self:
                order.access_url = '/my/orders/%s' % (order.id)
                
    def was_signed(self):
        _logger.info("--> signature: " + str(self.signature))
        return self.signature