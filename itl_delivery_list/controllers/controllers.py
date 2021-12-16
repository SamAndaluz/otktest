# -*- coding: utf-8 -*-
# from odoo import http


# class ItlDeliveryList(http.Controller):
#     @http.route('/itl_delivery_list/itl_delivery_list/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_delivery_list/itl_delivery_list/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_delivery_list.listing', {
#             'root': '/itl_delivery_list/itl_delivery_list',
#             'objects': http.request.env['itl_delivery_list.itl_delivery_list'].search([]),
#         })

#     @http.route('/itl_delivery_list/itl_delivery_list/objects/<model("itl_delivery_list.itl_delivery_list"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_delivery_list.object', {
#             'object': obj
#         })
