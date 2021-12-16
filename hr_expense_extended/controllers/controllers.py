# -*- coding: utf-8 -*-
# from odoo import http


# class HrExpenseExtended(http.Controller):
#     @http.route('/hr_expense_extended/hr_expense_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_expense_extended/hr_expense_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_expense_extended.listing', {
#             'root': '/hr_expense_extended/hr_expense_extended',
#             'objects': http.request.env['hr_expense_extended.hr_expense_extended'].search([]),
#         })

#     @http.route('/hr_expense_extended/hr_expense_extended/objects/<model("hr_expense_extended.hr_expense_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_expense_extended.object', {
#             'object': obj
#         })
