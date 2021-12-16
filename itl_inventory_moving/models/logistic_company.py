
from odoo import models, fields, api


class LogisticCompany(models.Model):
    _name = 'logistic.company'
    
    name = fields.Char()
    email = fields.Char()