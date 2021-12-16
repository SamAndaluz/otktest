# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalPurchase(http.Controller):
#     @http.route('/itl_approval_purchase/itl_approval_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_purchase/itl_approval_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_purchase.listing', {
#             'root': '/itl_approval_purchase/itl_approval_purchase',
#             'objects': http.request.env['itl_approval_purchase.itl_approval_purchase'].search([]),
#         })

#     @http.route('/itl_approval_purchase/itl_approval_purchase/objects/<model("itl_approval_purchase.itl_approval_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_purchase.object', {
#             'object': obj
#         })
