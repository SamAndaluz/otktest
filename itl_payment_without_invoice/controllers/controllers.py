# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPaymentWithoutInvoice(http.Controller):
#     @http.route('/itl_payment_without_invoice/itl_payment_without_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_payment_without_invoice/itl_payment_without_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_payment_without_invoice.listing', {
#             'root': '/itl_payment_without_invoice/itl_payment_without_invoice',
#             'objects': http.request.env['itl_payment_without_invoice.itl_payment_without_invoice'].search([]),
#         })

#     @http.route('/itl_payment_without_invoice/itl_payment_without_invoice/objects/<model("itl_payment_without_invoice.itl_payment_without_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_payment_without_invoice.object', {
#             'object': obj
#         })
