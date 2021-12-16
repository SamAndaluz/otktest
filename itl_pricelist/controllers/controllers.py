# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPricelist(http.Controller):
#     @http.route('/itl_pricelist/itl_pricelist/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_pricelist/itl_pricelist/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_pricelist.listing', {
#             'root': '/itl_pricelist/itl_pricelist',
#             'objects': http.request.env['itl_pricelist.itl_pricelist'].search([]),
#         })

#     @http.route('/itl_pricelist/itl_pricelist/objects/<model("itl_pricelist.itl_pricelist"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_pricelist.object', {
#             'object': obj
#         })
