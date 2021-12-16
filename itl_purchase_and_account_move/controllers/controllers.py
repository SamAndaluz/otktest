# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPurchaseAndAccountMove(http.Controller):
#     @http.route('/itl_purchase_and_account_move/itl_purchase_and_account_move/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_purchase_and_account_move/itl_purchase_and_account_move/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_purchase_and_account_move.listing', {
#             'root': '/itl_purchase_and_account_move/itl_purchase_and_account_move',
#             'objects': http.request.env['itl_purchase_and_account_move.itl_purchase_and_account_move'].search([]),
#         })

#     @http.route('/itl_purchase_and_account_move/itl_purchase_and_account_move/objects/<model("itl_purchase_and_account_move.itl_purchase_and_account_move"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_purchase_and_account_move.object', {
#             'object': obj
#         })
