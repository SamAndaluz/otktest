# -*- coding: utf-8 -*-
# from odoo import http


# class ItlL10nMxEdiExtended(http.Controller):
#     @http.route('/itl_l10n_mx_edi_extended/itl_l10n_mx_edi_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_l10n_mx_edi_extended/itl_l10n_mx_edi_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_l10n_mx_edi_extended.listing', {
#             'root': '/itl_l10n_mx_edi_extended/itl_l10n_mx_edi_extended',
#             'objects': http.request.env['itl_l10n_mx_edi_extended.itl_l10n_mx_edi_extended'].search([]),
#         })

#     @http.route('/itl_l10n_mx_edi_extended/itl_l10n_mx_edi_extended/objects/<model("itl_l10n_mx_edi_extended.itl_l10n_mx_edi_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_l10n_mx_edi_extended.object', {
#             'object': obj
#         })
