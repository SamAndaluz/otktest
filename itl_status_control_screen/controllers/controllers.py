# -*- coding: utf-8 -*-
# from odoo import http


# class ItlStatusControlScreen(http.Controller):
#     @http.route('/itl_status_control_screen/itl_status_control_screen/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_status_control_screen/itl_status_control_screen/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_status_control_screen.listing', {
#             'root': '/itl_status_control_screen/itl_status_control_screen',
#             'objects': http.request.env['itl_status_control_screen.itl_status_control_screen'].search([]),
#         })

#     @http.route('/itl_status_control_screen/itl_status_control_screen/objects/<model("itl_status_control_screen.itl_status_control_screen"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_status_control_screen.object', {
#             'object': obj
#         })
