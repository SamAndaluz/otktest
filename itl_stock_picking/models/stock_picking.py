from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class Picking(models.Model):
    _inherit = "stock.picking"
    
    # Inherit from stock module
    def action_done(self):
        result = super(Picking, self).action_done()
        if self.picking_type_id.code == 'outgoing' and self.sale_id:
            sale_id = self.sale_id
            partner_id = sale_id.partner_id.sudo()
            temporal_vat = False
            if sale_id.invoice_count == 0:
                if partner_id.vat:
                    temporal_vat = partner_id.vat
                if partner_id.itl_is_invoice_required:
                    if not partner_id.vat:
                        raise UserError("El contacto no tiene un RFC valido.")
                    if not partner_id.itl_payment_method_id:
                        raise UserError("El contacto no tiene forma de pago.")
                    if not partner_id.itl_usage:
                        raise UserError("El contacto no tiene uso de CFDI.")
                    if not partner_id.property_payment_term_id:
                        raise UserError("El contacto no tiene plazo de pago.")
                else:
                    temporal_vat = partner_id.vat
                    partner_id.vat = False
                itl_invoice = sale_id._create_invoices()
                partner_id.vat = temporal_vat

                msg = _("La factura fue creada y timbrada correctamente en la %s") % sale_id.name
                self.message_post(body=msg)
                
        return result