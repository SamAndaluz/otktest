# -*- coding: utf-8 -*-

import calendar
from dateutil.relativedelta import relativedelta
from math import copysign

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    company_partner_id = fields.Integer(related='company_id.partner_id.id', store=False)
    other_address_id = fields.Many2one('res.partner', string="Address")
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    
    asset_type_custom = fields.Selection([('transport','Transport equipment'),
                                  ('computer','Computer equipment'),
                                  ('office','Office equipment')], string="Asset type")
    tag_number = fields.Char(string="Tag number")
    
    # For vehicle
    plates_number = fields.Char(string="Plates number")
    
    # For computer
    serial_number = fields.Char(string="Serial number")
    
    # For office
    #asset_location = fields.Selection([('comedor','Comedor'),
    #                                  ('tatsus_office',"Tatsu's Office"),
    #                                  ('centro_trabajo_admon','Centros de Trabajo Admón'),
    #                                  ('meeting_room','Meeting Room'),
    #                                  ('jcs_room',"JC's Room"),
    #                                  ('warehouse','Warehouse')], string="Location")
    
    asset_location_id = fields.Many2one('asset.location', string="Location", domain="[('id','=',False)]")
    asset_quantity = fields.Integer(string="Quantity")
    
    @api.onchange('other_address_id')
    def onchange_other_address_id(self):
        res = {}
        if self.other_address_id:
            if self.other_address_id.asset_location_ids:
                #res['domain'] = [('id','in',self.other_address_id.asset_location_ids.ids)]
                return {'domain': {'asset_location_id': [('id','in',self.other_address_id.asset_location_ids.ids)]}}
            else:
                #res['domain'] = [('id','=',False)]
                return {'domain': {'asset_location_id': [('id','=',False)]}}
        else:
            #res['domain'] = [('name','=',False)]
            return {'domain': {'asset_location_id': [('id','=',False)]}}
                                   
    