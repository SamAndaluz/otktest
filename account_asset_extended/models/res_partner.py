from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'
    
    asset_location_ids = fields.Many2many('asset.location', string="Asset locations")
    
class AssetLocation(models.Model):
    _name = 'asset.location'
    _description = "Asset Location"
    
    name = fields.Char(string="Name")
    #partner_id = fields.Many2one('res.partner')