# -*- coding: utf-8 -*-
# from odoo import http


# class ItlJournalEntry(http.Controller):
#     @http.route('/itl_journal_entry/itl_journal_entry/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_journal_entry/itl_journal_entry/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_journal_entry.listing', {
#             'root': '/itl_journal_entry/itl_journal_entry',
#             'objects': http.request.env['itl_journal_entry.itl_journal_entry'].search([]),
#         })

#     @http.route('/itl_journal_entry/itl_journal_entry/objects/<model("itl_journal_entry.itl_journal_entry"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_journal_entry.object', {
#             'object': obj
#         })
