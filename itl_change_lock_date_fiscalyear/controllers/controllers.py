# -*- coding: utf-8 -*-
# from odoo import http


# class ItlChangeLockDateFiscalyear(http.Controller):
#     @http.route('/itl_change_lock_date_fiscalyear/itl_change_lock_date_fiscalyear/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_change_lock_date_fiscalyear/itl_change_lock_date_fiscalyear/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_change_lock_date_fiscalyear.listing', {
#             'root': '/itl_change_lock_date_fiscalyear/itl_change_lock_date_fiscalyear',
#             'objects': http.request.env['itl_change_lock_date_fiscalyear.itl_change_lock_date_fiscalyear'].search([]),
#         })

#     @http.route('/itl_change_lock_date_fiscalyear/itl_change_lock_date_fiscalyear/objects/<model("itl_change_lock_date_fiscalyear.itl_change_lock_date_fiscalyear"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_change_lock_date_fiscalyear.object', {
#             'object': obj
#         })
