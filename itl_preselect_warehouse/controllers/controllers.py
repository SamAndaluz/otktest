# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPreselectWarehouse(http.Controller):
#     @http.route('/itl_preselect_warehouse/itl_preselect_warehouse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_preselect_warehouse/itl_preselect_warehouse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_preselect_warehouse.listing', {
#             'root': '/itl_preselect_warehouse/itl_preselect_warehouse',
#             'objects': http.request.env['itl_preselect_warehouse.itl_preselect_warehouse'].search([]),
#         })

#     @http.route('/itl_preselect_warehouse/itl_preselect_warehouse/objects/<model("itl_preselect_warehouse.itl_preselect_warehouse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_preselect_warehouse.object', {
#             'object': obj
#         })
