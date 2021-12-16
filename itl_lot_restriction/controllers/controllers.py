# -*- coding: utf-8 -*-
# from odoo import http


# class ItlLotRestriction(http.Controller):
#     @http.route('/itl_lot_restriction/itl_lot_restriction/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_lot_restriction/itl_lot_restriction/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_lot_restriction.listing', {
#             'root': '/itl_lot_restriction/itl_lot_restriction',
#             'objects': http.request.env['itl_lot_restriction.itl_lot_restriction'].search([]),
#         })

#     @http.route('/itl_lot_restriction/itl_lot_restriction/objects/<model("itl_lot_restriction.itl_lot_restriction"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_lot_restriction.object', {
#             'object': obj
#         })
