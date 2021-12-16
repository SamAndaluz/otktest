from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        _logger.info("--> onchange_partner_id")
        super(SaleOrder, self).onchange_partner_id()
        partners_invoice = []
        partners_shipping = []
        domain = {}
        for record in self:
            if record.partner_id:
                if record.partner_id.child_ids:
                    for partner in record.partner_id.child_ids:
                        if partner.type == 'invoice':
                            partners_invoice.append(partner.id)
                        if partner.type == 'delivery':
                            partners_shipping.append(partner.id)
                if partners_invoice:
                    domain['partner_invoice_id'] =  [('id', 'in', partners_invoice)]
                else:
                    domain['partner_invoice_id'] =  [('id', 'in', [record.partner_id.id])]
                if partners_shipping:
                    domain['partner_shipping_id'] = [('id', 'in', partners_shipping)]
                else:
                    domain['partner_shipping_id'] =  [('id', 'in', [record.partner_id.id])]
            else:
                domain['partner_invoice_id'] =  [('type', '=', 'invoice')]
                domain['partner_shipping_id'] =  [('type', '=', 'delivery')]

        _logger.info("--> domain: " + str(domain))
        return {'domain': domain}
