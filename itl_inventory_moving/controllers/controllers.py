#-*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import werkzeug.utils

import logging
_logger = logging.getLogger(__name__)

class ItlInventoryMoving(http.Controller):
    @http.route('/itl_inventory_moving/show_moves', auth='public')
    def index(self, **kw):
        _logger.info("###> itl_inventory_moving controller")
        _logger.info("###> **kw: " + str(type(kw.get('active_ids', 1))))
        active_ids = json.loads(kw.get('active_ids', 1))
        _logger.info("###> active_ids: " + str(type(active_ids)))
        
        action_id = http.request.env.ref('itl_inventory_moving.itl_vpicktree_filtered')
        return werkzeug.utils.redirect('/web?view_type=list&model=stock.picking&action=%s' %(action_id.id))

#     @http.route('/itl_inventory_moving/itl_inventory_moving/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_inventory_moving.listing', {
#             'root': '/itl_inventory_moving/itl_inventory_moving',
#             'objects': http.request.env['itl_inventory_moving.itl_inventory_moving'].search([]),
#         })

#     @http.route('/itl_inventory_moving/itl_inventory_moving/objects/<model("itl_inventory_moving.itl_inventory_moving"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_inventory_moving.object', {
#             'object': obj
#         })
