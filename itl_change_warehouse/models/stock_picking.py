# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"
    
    
    def change_warehouse(self):
        flag = self.env.user.has_group('itl_change_warehouse.group_itl_change_warehouse')
        if not flag:
            raise ValidationError("You are not allowed to change warehouse.")
        view = self.env.ref('itl_change_warehouse.itl_change_warehouse_form')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['picking_ids'] = context.get('active_ids') if 'active_model' in context and context.get('active_model') == 'stock.picking' else self.ids
        return {
            'name': 'Change Warehouse',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.change.warehouse',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }