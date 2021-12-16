# -*- coding: utf-8 -*-
# from odoo import http


# class AssestsExtended(http.Controller):
#     @http.route('/assests_extended/assests_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/assests_extended/assests_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('assests_extended.listing', {
#             'root': '/assests_extended/assests_extended',
#             'objects': http.request.env['assests_extended.assests_extended'].search([]),
#         })

#     @http.route('/assests_extended/assests_extended/objects/<model("assests_extended.assests_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('assests_extended.object', {
#             'object': obj
#         })
