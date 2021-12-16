# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class itl_approval_vendor_bill(models.Model):
#     _name = 'itl_approval_vendor_bill.itl_approval_vendor_bill'
#     _description = 'itl_approval_vendor_bill.itl_approval_vendor_bill'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
