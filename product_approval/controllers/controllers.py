# -*- coding: utf-8 -*-
# from odoo import http


# class ProductApproval(http.Controller):
#     @http.route('/product_approval/product_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_approval/product_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_approval.listing', {
#             'root': '/product_approval/product_approval',
#             'objects': http.request.env['product_approval.product_approval'].search([]),
#         })

#     @http.route('/product_approval/product_approval/objects/<model("product_approval.product_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_approval.object', {
#             'object': obj
#         })
