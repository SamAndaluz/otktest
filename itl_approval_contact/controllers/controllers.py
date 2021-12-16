# -*- coding: utf-8 -*-
# from odoo import http


# class ItlApprovalContact(http.Controller):
#     @http.route('/itl_approval_contact/itl_approval_contact/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_approval_contact/itl_approval_contact/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_approval_contact.listing', {
#             'root': '/itl_approval_contact/itl_approval_contact',
#             'objects': http.request.env['itl_approval_contact.itl_approval_contact'].search([]),
#         })

#     @http.route('/itl_approval_contact/itl_approval_contact/objects/<model("itl_approval_contact.itl_approval_contact"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_approval_contact.object', {
#             'object': obj
#         })
