# -*- coding: utf-8 -*-
# from odoo import http


# class CapitalizationPolicy(http.Controller):
#     @http.route('/capitalization_policy/capitalization_policy/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/capitalization_policy/capitalization_policy/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('capitalization_policy.listing', {
#             'root': '/capitalization_policy/capitalization_policy',
#             'objects': http.request.env['capitalization_policy.capitalization_policy'].search([]),
#         })

#     @http.route('/capitalization_policy/capitalization_policy/objects/<model("capitalization_policy.capitalization_policy"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('capitalization_policy.object', {
#             'object': obj
#         })
