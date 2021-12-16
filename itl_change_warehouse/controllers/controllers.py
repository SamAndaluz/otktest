# -*- coding: utf-8 -*-
# from odoo import http


# class ItlChangeWarehouse(http.Controller):
#     @http.route('/itl_change_warehouse/itl_change_warehouse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_change_warehouse/itl_change_warehouse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_change_warehouse.listing', {
#             'root': '/itl_change_warehouse/itl_change_warehouse',
#             'objects': http.request.env['itl_change_warehouse.itl_change_warehouse'].search([]),
#         })

#     @http.route('/itl_change_warehouse/itl_change_warehouse/objects/<model("itl_change_warehouse.itl_change_warehouse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_change_warehouse.object', {
#             'object': obj
#         })
