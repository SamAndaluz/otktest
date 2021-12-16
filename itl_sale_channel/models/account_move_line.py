from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class AccountMoveCustom(models.Model):
    _inherit = 'account.move'
    

    @api.model
    def create(self, vals):
        partner_id = False
        if 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals['partner_id'])
        
        if partner_id and partner_id.sale_channel_id and 'invoice_line_ids' in vals:
            for line in vals['invoice_line_ids']:
                line[2]['analytic_account_id'] = partner_id.sale_channel_id.analytic_account_id.id
            
        
        record = super(AccountMoveCustom, self).create(vals)
        
        return record