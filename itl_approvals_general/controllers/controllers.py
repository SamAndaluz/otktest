# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalsGeneral(http.Controller):
#     @http.route('/itl_approvals_general/itl_approvals_general/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approvals_general/itl_approvals_general/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approvals_general.listing', {
#             'root': '/itl_approvals_general/itl_approvals_general',
#             'objects': http.request.env['itl_approvals_general.itl_approvals_general'].search([]),
#         })

#     @http.route('/itl_approvals_general/itl_approvals_general/objects/<model("itl_approvals_general.itl_approvals_general"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approvals_general.object', {
#             'object': obj
#         })
