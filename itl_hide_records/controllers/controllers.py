# -*- coding: utf-8 -*-
# from odoo import http


# class ItlHideRecords(http.Controller):
#     @http.route('/itl_hide_records/itl_hide_records/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_hide_records/itl_hide_records/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_hide_records.listing', {
#             'root': '/itl_hide_records/itl_hide_records',
#             'objects': http.request.env['itl_hide_records.itl_hide_records'].search([]),
#         })

#     @http.route('/itl_hide_records/itl_hide_records/objects/<model("itl_hide_records.itl_hide_records"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_hide_records.object', {
#             'object': obj
#         })
