from odoo import models, fields, api


class StockInventoryLine(models.Model):
    _name = 'stock.inventory.line'
    _inherit = ['stock.inventory.line']

    was_filled = fields.Boolean(
        string="Was filled", default=False, help="If is checked it means that the product_qty " +
        "was already filled (this field also is used to allow extra modifications when is unchecked).")

    prefilled_qty = fields.Selection(
        related='inventory_id.prefill_counted_quantity', string="Prefilled option",
        store=True, readonly=True, related_sudo=False)

    damaged_product_qty = fields.Float(
        'Damaged Products Quantity', digits=0, copy=False, store=True)
    stored_difference_qty = fields.Float(
        "Difference", digits=0, copy=False, store=True, compute="_compute_stored_diff"
    )

    # This field is just to be used on domain condition
    tracking = fields.Selection(related='product_id.tracking', String="Tracking", store=False)

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        #  here we check if product_qty was already set and then protect that field
        #  for extra modification. (modifications can be done if was_filled checkbox is unchecked)
        if self.prefilled_qty == 'counted':
            if self.theoretical_qty != self.product_qty:
                self.was_filled = True
        if self.prefilled_qty == 'zero':
            if self.theoretical_qty != self.product_qty:
                self.was_filled = True

    @api.depends('product_qty', 'theoretical_qty', 'damaged_product_qty')
    def _compute_difference(self):
        for line in self:
            line.difference_qty = line.product_qty - line.theoretical_qty + line.damaged_product_qty

    @api.depends('difference_qty')
    def _compute_stored_diff(self):
        for record in self:
            record.stored_difference_qty = record.difference_qty