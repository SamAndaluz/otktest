# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInternalTransfer(http.Controller):
#     @http.route('/itl_internal_transfer/itl_internal_transfer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_internal_transfer/itl_internal_transfer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_internal_transfer.listing', {
#             'root': '/itl_internal_transfer/itl_internal_transfer',
#             'objects': http.request.env['itl_internal_transfer.itl_internal_transfer'].search([]),
#         })

#     @http.route('/itl_internal_transfer/itl_internal_transfer/objects/<model("itl_internal_transfer.itl_internal_transfer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_internal_transfer.object', {
#             'object': obj
#         })
