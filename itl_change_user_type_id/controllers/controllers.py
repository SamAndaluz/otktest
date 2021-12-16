# -*- coding: utf-8 -*-
# from odoo import http


# class ItlChangeUserTypeId(http.Controller):
#     @http.route('/itl_change_user_type_id/itl_change_user_type_id/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_change_user_type_id/itl_change_user_type_id/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_change_user_type_id.listing', {
#             'root': '/itl_change_user_type_id/itl_change_user_type_id',
#             'objects': http.request.env['itl_change_user_type_id.itl_change_user_type_id'].search([]),
#         })

#     @http.route('/itl_change_user_type_id/itl_change_user_type_id/objects/<model("itl_change_user_type_id.itl_change_user_type_id"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_change_user_type_id.object', {
#             'object': obj
#         })
