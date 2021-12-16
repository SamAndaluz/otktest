# -*- coding: utf-8 -*-
# from odoo import http


# class ItlUserManagers(http.Controller):
#     @http.route('/itl_user_managers/itl_user_managers/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_user_managers/itl_user_managers/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_user_managers.listing', {
#             'root': '/itl_user_managers/itl_user_managers',
#             'objects': http.request.env['itl_user_managers.itl_user_managers'].search([]),
#         })

#     @http.route('/itl_user_managers/itl_user_managers/objects/<model("itl_user_managers.itl_user_managers"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_user_managers.object', {
#             'object': obj
#         })
