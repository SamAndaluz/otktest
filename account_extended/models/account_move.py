# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLineCustom(models.Model):
    _inherit = "account.move.line"

    name_legacy = fields.Char(string="Label legacy")
    