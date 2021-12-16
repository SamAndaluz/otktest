# -*- coding: utf-8 -*-
# from odoo import http


# class ItlSaleOrderType(http.Controller):
#     @http.route('/itl_sale_order_type/itl_sale_order_type/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_sale_order_type/itl_sale_order_type/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_sale_order_type.listing', {
#             'root': '/itl_sale_order_type/itl_sale_order_type',
#             'objects': http.request.env['itl_sale_order_type.itl_sale_order_type'].search([]),
#         })

#     @http.route('/itl_sale_order_type/itl_sale_order_type/objects/<model("itl_sale_order_type.itl_sale_order_type"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_sale_order_type.object', {
#             'object': obj
#         })
