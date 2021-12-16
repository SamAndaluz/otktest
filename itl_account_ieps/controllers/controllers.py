# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAccountIeps(http.Controller):
#     @http.route('/itl_account_ieps/itl_account_ieps/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_account_ieps/itl_account_ieps/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_account_ieps.listing', {
#             'root': '/itl_account_ieps/itl_account_ieps',
#             'objects': http.request.env['itl_account_ieps.itl_account_ieps'].search([]),
#         })

#     @http.route('/itl_account_ieps/itl_account_ieps/objects/<model("itl_account_ieps.itl_account_ieps"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_account_ieps.object', {
#             'object': obj
#         })
