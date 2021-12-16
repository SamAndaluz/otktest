# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPurchaseOrder(http.Controller):
#     @http.route('/itl_purchase_order/itl_purchase_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_purchase_order/itl_purchase_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_purchase_order.listing', {
#             'root': '/itl_purchase_order/itl_purchase_order',
#             'objects': http.request.env['itl_purchase_order.itl_purchase_order'].search([]),
#         })

#     @http.route('/itl_purchase_order/itl_purchase_order/objects/<model("itl_purchase_order.itl_purchase_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_purchase_order.object', {
#             'object': obj
#         })
