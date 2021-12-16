
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalProductLine(models.Model):
    _name = 'approval.product.line'
    _description = 'Product Line'

    _check_company_auto = True

    approval_request_id = fields.Many2one('approval.request', required=True, ondelete='cascade')
    description = fields.Char("Description", required=True)
    company_id = fields.Many2one(string='Company', related='approval_request_id.company_id', store=True, readonly=True, index=True)
    product_id = fields.Many2one('product.product', string="Products", check_company=True)
    product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    quantity = fields.Float("Quantity", default=1.0)
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Serial Number")

    ####
    product_price = fields.Float(string="Product price")
    product_doc_price = fields.Float(string="Document product price")
    product_discount = fields.Float(string="Discount")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
            if not self.description:
                self.description = self.product_id.display_name
        else:
            self.product_uom_id = None
