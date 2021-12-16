# -*- coding: utf-8 -*-
# from odoo import http


# class ItlSaleChannel(http.Controller):
#     @http.route('/itl_sale_channel/itl_sale_channel/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_sale_channel/itl_sale_channel/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_sale_channel.listing', {
#             'root': '/itl_sale_channel/itl_sale_channel',
#             'objects': http.request.env['itl_sale_channel.itl_sale_channel'].search([]),
#         })

#     @http.route('/itl_sale_channel/itl_sale_channel/objects/<model("itl_sale_channel.itl_sale_channel"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_sale_channel.object', {
#             'object': obj
#         })
