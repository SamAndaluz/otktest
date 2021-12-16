from itertools import chain

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr
from odoo.tools.misc import get_lang


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    
    # Inherit field 
    compute_price = fields.Selection(selection_add=[('fixed_formula', 'Fixed Formula')])
    
    itl_gross = fields.Float(string="Gross sales", digits='Product Price')
    itl_discount = fields.Float(string="Discount", digits='Product Price')
    itl_distribution_fee = fields.Float(string="Distribution fee", digits='Product Price')
    itl_other_discount = fields.Float(string="Other discount", digits='Product Price')
    itl_fixed_price = fields.Float(string="New fixed price", compute="_compute_itl_fixed_price")
    itl_current_fixed_price = fields.Float(string="Current fixed price", readonly=True, store=True, default=0)
    itl_price_has_changes = fields.Boolean(compute="_check_if_price_has_changes")
    
    approval_ids = fields.One2many('approval.request', 'pricelist_item_id')
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_approval_status")
    
    def _compute_approval_status(self):
        for item in self:
            item.approval_status = False
            if len(item.approval_ids) > 0:
                last_request = item.approval_ids[-1]
                item.approval_status = last_request.request_status
    
    @api.onchange('itl_fixed_price')
    def onchange_itl_fixed_price(self):
        self.itl_price_has_changes = False
        if self.itl_current_fixed_price != self.itl_fixed_price:
            self.itl_price_has_changes = True
    
    def _check_if_price_has_changes(self):
        self.itl_price_has_changes = False
        if self.itl_current_fixed_price != self.itl_fixed_price:
            self.itl_price_has_changes = True
            
    def send_to_approve(self):
        if not self.env.company.itl_pricelist_approval_category_id:
            raise ValidationError("Approval category is not configured.")

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Pricelist - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_pricelist_approval_category_id.id,
            'pricelist_item_id': self.id,
        }

        rec = approval_obj.create(vals)
        rec._onchange_category_id()
        rec.action_confirm()
        #if not self.approval_request_id:
        #    rec = approval_obj.create(vals)
        #    rec._onchange_category_id()
        #    rec.action_confirm()
        #else:
        #    rec = self.approval_request_id
        #    for p in rec.product_line_ids:
        #        p.unlink()
        #    rec.write(vals)
        #    rec.action_draft()
        #    rec.action_confirm()
        approvals = self.approval_ids
        approvals += rec
        self.approval_ids = [(6, 0, approvals.ids)]

        #self.state = 'to_approve'

        #self.message_post_with_view('itl_approval_contact.message_approval_contact_created_link',
        #            values={'self': rec, 'origin': self},
        #            subtype_id=self.env.ref('mail.mt_note').id)

        #rec.message_post_with_view('mail.message_origin_link',
        #            values={'self': rec, 'origin': self},
        #            subtype_id=self.env.ref('mail.mt_note').id)
    
    @api.depends('itl_gross','itl_discount','itl_distribution_fee','itl_other_discount')
    def _compute_itl_fixed_price(self):
        self.itl_fixed_price = self.itl_gross - self.itl_discount - self.itl_distribution_fee - self.itl_other_discount
    
    # Inherit
    def _get_pricelist_item_name_price(self):
        super(PricelistItem, self)._get_pricelist_item_name_price()
        
        for item in self:
            if item.compute_price == 'fixed_formula':
                decimal_places = self.env['decimal.precision'].precision_get('Product Price')
                item.price = "%s %s" % (
                        float_repr(
                            item.itl_current_fixed_price,
                            decimal_places,
                        ),
                        item.currency_id.symbol,
                    )
    
    # Inherit
    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        """Compute the unit price of a product in the context of a pricelist application.
           The unused parameters are there to make the full context available for overrides.
        """
        self.ensure_one()
        
        if self.compute_price == 'fixed_formula':
            # Fixed Price = Gross Sales Price - Discount - Distribution Fee - Other Discount
            price = self.itl_current_fixed_price
        else:
            price = super(PricelistItem, self)._compute_price(price, price_uom, product, quantity, partner)
        
        return price