# -*- coding: utf-8 -*-
# from odoo import http


# class ItlSaleOrder(http.Controller):
#     @http.route('/itl_sale_order/itl_sale_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_sale_order/itl_sale_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_sale_order.listing', {
#             'root': '/itl_sale_order/itl_sale_order',
#             'objects': http.request.env['itl_sale_order.itl_sale_order'].search([]),
#         })

#     @http.route('/itl_sale_order/itl_sale_order/objects/<model("itl_sale_order.itl_sale_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_sale_order.object', {
#             'object': obj
#         })
