# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInvoicePurchaseRelation(http.Controller):
#     @http.route('/itl_invoice_purchase_relation/itl_invoice_purchase_relation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_invoice_purchase_relation/itl_invoice_purchase_relation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_invoice_purchase_relation.listing', {
#             'root': '/itl_invoice_purchase_relation/itl_invoice_purchase_relation',
#             'objects': http.request.env['itl_invoice_purchase_relation.itl_invoice_purchase_relation'].search([]),
#         })

#     @http.route('/itl_invoice_purchase_relation/itl_invoice_purchase_relation/objects/<model("itl_invoice_purchase_relation.itl_invoice_purchase_relation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_invoice_purchase_relation.object', {
#             'object': obj
#         })
