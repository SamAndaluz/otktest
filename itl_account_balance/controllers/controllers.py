# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAccountBalance(http.Controller):
#     @http.route('/itl_account_balance/itl_account_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_account_balance/itl_account_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_account_balance.listing', {
#             'root': '/itl_account_balance/itl_account_balance',
#             'objects': http.request.env['itl_account_balance.itl_account_balance'].search([]),
#         })

#     @http.route('/itl_account_balance/itl_account_balance/objects/<model("itl_account_balance.itl_account_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_account_balance.object', {
#             'object': obj
#         })
