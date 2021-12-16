# -*- coding: utf-8 -*-
# from odoo import http


# class ItlInvoiceApproval(http.Controller):
#     @http.route('/itl_invoice_approval/itl_invoice_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_invoice_approval/itl_invoice_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_invoice_approval.listing', {
#             'root': '/itl_invoice_approval/itl_invoice_approval',
#             'objects': http.request.env['itl_invoice_approval.itl_invoice_approval'].search([]),
#         })

#     @http.route('/itl_invoice_approval/itl_invoice_approval/objects/<model("itl_invoice_approval.itl_invoice_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_invoice_approval.object', {
#             'object': obj
#         })
