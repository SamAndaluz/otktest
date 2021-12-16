# -*- coding: utf-8 -*-
# from odoo import http


# class ItlMonthlyAverageCost(http.Controller):
#     @http.route('/itl_monthly_average_cost/itl_monthly_average_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itl_monthly_average_cost/itl_monthly_average_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itl_monthly_average_cost.listing', {
#             'root': '/itl_monthly_average_cost/itl_monthly_average_cost',
#             'objects': http.request.env['itl_monthly_average_cost.itl_monthly_average_cost'].search([]),
#         })

#     @http.route('/itl_monthly_average_cost/itl_monthly_average_cost/objects/<model("itl_monthly_average_cost.itl_monthly_average_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itl_monthly_average_cost.object', {
#             'object': obj
#         })
