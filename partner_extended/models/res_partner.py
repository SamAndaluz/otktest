# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class partner_extended(models.Model):
    _inherit = 'res.partner'
    #_description = 'partner extended'
    
    
    is_customer = fields.Boolean(string="Is customer")
    is_vendor = fields.Boolean(string="Is vendor")
    
    l10n_mx_type_of_operation = fields.Selection(selection_add=[
        ('04', ' 04 - Proveedor Nacional'),
        ('05', ' 05 - Proveedor Extranjero')],
        help='Indicate the operations type that makes this supplier. Is the '
        'second column in DIOT report')
    
    hide_action_buttons = fields.Boolean('Hide Action Buttons', compute='_compute_hide_action_buttons')
    hide_action_buttons_html = fields.Html(
                                            string='CSS',
                                            sanitize=False,
                                            compute='_compute_hide_action_buttons',
                                            store=False,
                                        )
    
    
    @api.depends('is_vendor','is_customer')
    def _compute_hide_action_buttons(self):
        for partner in self:
            partner.hide_action_buttons_html = ''
            if not partner.is_customer and not partner.is_vendor:
                partner.hide_action_buttons = False
            elif partner.is_customer and partner.is_vendor:
                if self.env.user.has_group('partner_extended.group_set_is_customer') and self.env.user.has_group('partner_extended.group_set_is_vendor'):
                    partner.hide_action_buttons = False
                else:
                    partner.hide_action_buttons = True
                    partner.hide_action_buttons_html = '<style>.o_form_button_edit {display: none !important;}</style>'
            elif self.env.user.has_group('partner_extended.group_set_is_customer') and partner.is_customer:
                partner.hide_action_buttons = False
            elif self.env.user.has_group('partner_extended.group_set_is_vendor') and partner.is_vendor:
                partner.hide_action_buttons = False
            else:
                partner.hide_action_buttons_html = '<style>.o_form_button_edit {display: none !important;}</style>'
                partner.hide_action_buttons = True
                
    
    #def write(self, vals):
    #    if self.hide_action_buttons and self.is_customer:
    #        raise ValidationError("No tiene permitido editar un contacto cliente.")
    #    if self.hide_action_buttons and self.is_vendor:
    #        raise ValidationError("No tiene permitido editar un contacto proveedor.")
    #        
    #    res = super(partner_extended, self).write(vals)
    #    
    #    return res
    