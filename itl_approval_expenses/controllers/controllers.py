# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalExpenses(http.Controller):
#     @http.route('/itl_approval_expenses/itl_approval_expenses/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_expenses/itl_approval_expenses/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_expenses.listing', {
#             'root': '/itl_approval_expenses/itl_approval_expenses',
#             'objects': http.request.env['itl_approval_expenses.itl_approval_expenses'].search([]),
#         })

#     @http.route('/itl_approval_expenses/itl_approval_expenses/objects/<model("itl_approval_expenses.itl_approval_expenses"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_expenses.object', {
#             'object': obj
#         })
