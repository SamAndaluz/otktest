# -*- coding: utf-8 -*-
# from odoo import http


# class ItlExportBankFormat(http.Controller):
#     @http.route('/itl_export_bank_format/itl_export_bank_format/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_export_bank_format/itl_export_bank_format/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_export_bank_format.listing', {
#             'root': '/itl_export_bank_format/itl_export_bank_format',
#             'objects': http.request.env['itl_export_bank_format.itl_export_bank_format'].search([]),
#         })

#     @http.route('/itl_export_bank_format/itl_export_bank_format/objects/<model("itl_export_bank_format.itl_export_bank_format"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_export_bank_format.object', {
#             'object': obj
#         })
