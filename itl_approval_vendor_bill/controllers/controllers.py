# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalVendorBill(http.Controller):
#     @http.route('/itl_approval_vendor_bill/itl_approval_vendor_bill/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_vendor_bill/itl_approval_vendor_bill/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_vendor_bill.listing', {
#             'root': '/itl_approval_vendor_bill/itl_approval_vendor_bill',
#             'objects': http.request.env['itl_approval_vendor_bill.itl_approval_vendor_bill'].search([]),
#         })

#     @http.route('/itl_approval_vendor_bill/itl_approval_vendor_bill/objects/<model("itl_approval_vendor_bill.itl_approval_vendor_bill"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_vendor_bill.object', {
#             'object': obj
#         })
