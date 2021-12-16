from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    itl_ped_purchase_deposit_default_product_id = fields.Many2one(
        comodel_name="product.product",
        string="ITL Purchase Deposit Product for Pedimento",
        domain=[("type", "=", "service")],
        help="Default product used for down payment (Pedimento).",
        config_parameter='itl_ped_purchase_deposit_default_product_id',
    )
    
    itl_inv_purchase_deposit_default_product_id = fields.Many2one(
        comodel_name="product.product",
        string="ITL Purchase Deposit Product for Foreign Invoice",
        domain=[("type", "=", "service")],
        help="Default product used for down payment (Foreign invoice).",
        config_parameter='itl_inv_purchase_deposit_default_product_id',
    )
