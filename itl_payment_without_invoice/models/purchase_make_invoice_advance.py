import time
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)

class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"
    
    
    def itl_create_invoices(self):
        Purchase = self.env["purchase.order"]
        IrDefault = self.env["ir.default"].sudo()
        purchases = Purchase.browse(self._context.get("active_ids", []))
        # Create deposit product if necessary
        product = self.purchase_deposit_product_id
        if not product:
            raise UserError("The product used to invoice a down payment is not configured.")
        PurchaseLine = self.env["purchase.order.line"]
        invoices = []
        for order in purchases:
            amount = self.amount
            if self.advance_payment_method == "percentage":  # Case percent
                amount = self.amount / 100 * order.amount_untaxed
            if product.purchase_method != "purchase":
                raise UserError(
                    _(
                        "The product used to invoice a down payment should have "
                        'an invoice policy set to "Ordered quantities". '
                        "Please update your deposit product to be able to "
                        "create a deposit invoice."
                    )
                )
            if product.type != "service":
                raise UserError(
                    _(
                        "The product used to invoice a down payment should be "
                        'of type "Service". Please use another product or '
                        "update this product."
                    )
                )
            taxes = product.supplier_taxes_id.filtered(
                lambda r: not order.company_id or r.company_id == order.company_id
            )
            if order.fiscal_position_id and taxes:
                tax_ids = order.fiscal_position_id.map_tax(taxes).ids
            else:
                tax_ids = taxes.ids
            context = {"lang": order.partner_id.lang}
            po_line = PurchaseLine.create(
                {
                    "name": _("Advance: %s") % (time.strftime("%m %Y"),),
                    "price_unit": amount,
                    "product_qty": 0.0,
                    "order_id": order.id,
                    "product_uom": product.uom_id.id,
                    "product_id": product.id,
                    "taxes_id": [(6, 0, tax_ids)],
                    "date_planned": datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT
                    ),
                    "is_deposit": True,
                }
            )
            del context
            invoices.append(self._create_invoice(order, po_line, amount))
            
        return invoices