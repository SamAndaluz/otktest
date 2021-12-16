# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class itl_invoice_expenses_relation(models.Model):
#     _name = 'itl_invoice_expenses_relation.itl_invoice_expenses_relation'
#     _description = 'itl_invoice_expenses_relation.itl_invoice_expenses_relation'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
