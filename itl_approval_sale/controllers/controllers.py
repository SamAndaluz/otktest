# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalSale(http.Controller):
#     @http.route('/itl_approval_sale/itl_approval_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_sale/itl_approval_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_sale.listing', {
#             'root': '/itl_approval_sale/itl_approval_sale',
#             'objects': http.request.env['itl_approval_sale.itl_approval_sale'].search([]),
#         })

#     @http.route('/itl_approval_sale/itl_approval_sale/objects/<model("itl_approval_sale.itl_approval_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_sale.object', {
#             'object': obj
#         })
