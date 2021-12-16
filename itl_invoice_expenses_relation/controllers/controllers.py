# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInvoiceExpensesRelation(http.Controller):
#     @http.route('/itl_invoice_expenses_relation/itl_invoice_expenses_relation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_invoice_expenses_relation/itl_invoice_expenses_relation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_invoice_expenses_relation.listing', {
#             'root': '/itl_invoice_expenses_relation/itl_invoice_expenses_relation',
#             'objects': http.request.env['itl_invoice_expenses_relation.itl_invoice_expenses_relation'].search([]),
#         })

#     @http.route('/itl_invoice_expenses_relation/itl_invoice_expenses_relation/objects/<model("itl_invoice_expenses_relation.itl_invoice_expenses_relation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_invoice_expenses_relation.object', {
#             'object': obj
#         })
