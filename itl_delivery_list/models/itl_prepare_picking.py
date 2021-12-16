# -*- coding: utf-8 -*-

from odoo import models, fields, api


class itl_delivery_list(models.TransientModel):
    _inherit = 'itl.prepare.picking'
    
    
    def generate_delivery_list(self):
        self.process_picking()
        report_action = self.env.ref('itl_delivery_list.delivery_list_report').report_action(self)
        report_action['close_on_report_download'] = True
        return report_action
