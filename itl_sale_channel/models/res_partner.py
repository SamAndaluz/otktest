
from odoo import models, fields, api


class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'
     
    sale_channel_id = fields.Many2one('sale.channel', string="Sale channel")

    @api.onchange('sale_channel_id')
    def _onchange_sale_channel_id(self):
        if self.sale_channel_id:
            if self.sale_channel_id.price_list_id:
                self.property_product_pricelist = self.sale_channel_id.price_list_id.id
