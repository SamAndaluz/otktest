# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class itl_change_lock_date_fiscalyear(models.Model):
#     _name = 'itl_change_lock_date_fiscalyear.itl_change_lock_date_fiscalyear'
#     _description = 'itl_change_lock_date_fiscalyear.itl_change_lock_date_fiscalyear'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
