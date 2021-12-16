# -*- coding: utf-8 -*-
# from odoo import http


# class ItlDeleteInvoice(http.Controller):
#     @http.route('/itl_delete_invoice/itl_delete_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_delete_invoice/itl_delete_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_delete_invoice.listing', {
#             'root': '/itl_delete_invoice/itl_delete_invoice',
#             'objects': http.request.env['itl_delete_invoice.itl_delete_invoice'].search([]),
#         })

#     @http.route('/itl_delete_invoice/itl_delete_invoice/objects/<model("itl_delete_invoice.itl_delete_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_delete_invoice.object', {
#             'object': obj
#         })
