# -*- coding: utf-8 -*-
# from odoo import http


# class ItlAccountReconciliation(http.Controller):
#     @http.route('/itl_account_reconciliation/itl_account_reconciliation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_account_reconciliation/itl_account_reconciliation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_account_reconciliation.listing', {
#             'root': '/itl_account_reconciliation/itl_account_reconciliation',
#             'objects': http.request.env['itl_account_reconciliation.itl_account_reconciliation'].search([]),
#         })

#     @http.route('/itl_account_reconciliation/itl_account_reconciliation/objects/<model("itl_account_reconciliation.itl_account_reconciliation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_account_reconciliation.object', {
#             'object': obj
#         })
