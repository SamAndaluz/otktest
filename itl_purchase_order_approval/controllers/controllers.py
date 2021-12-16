# -*- coding: utf-8 -*-
# from odoo import http


# class ItlPurchaseOrderApproval(http.Controller):
#     @http.route('/itl_purchase_order_approval/itl_purchase_order_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_purchase_order_approval/itl_purchase_order_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_purchase_order_approval.listing', {
#             'root': '/itl_purchase_order_approval/itl_purchase_order_approval',
#             'objects': http.request.env['itl_purchase_order_approval.itl_purchase_order_approval'].search([]),
#         })

#     @http.route('/itl_purchase_order_approval/itl_purchase_order_approval/objects/<model("itl_purchase_order_approval.itl_purchase_order_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_purchase_order_approval.object', {
#             'object': obj
#         })
