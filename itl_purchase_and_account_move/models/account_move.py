from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class AccountMoveInherit(models.Model):
    _inherit = "account.move"
    
    received_products = fields.Boolean(string="Products have been received in PO", compute="_get_purchase_received_products")
    
    @api.depends('invoice_origin')
    def _get_purchase_received_products(self):
        #if self.invoice_origin and self.type in ['in_invoice']:
        #    refs = self._get_invoice_po_reference()
        #else:
        #    self.received_products = True
            
        self._get_invoice_po_reference()
    
    def _get_invoice_po_reference(self):
        self.ensure_one()
        #vendor_refs = [ref for ref in set(self.line_ids.mapped('purchase_line_id.order_id')) if ref]
        received_products = any(self.line_ids.mapped('purchase_line_id.order_id.received_products'))
        received_products_manual = any(self.line_ids.mapped('purchase_line_id.order_id.received_products_manual'))
        if received_products or received_products_manual:
            self.received_products = True
        else:
            self.received_products = False
            
#    def action_post(self, force=False):
#        p_l = self.line_ids.mapped('purchase_line_id.order_id.order_line')
#        _logger.info("-> p_l: " + str(p_l))
#        for invoice_line in self.invoice_line_ids:
#            if invoice_line.purchase_line_id and invoice_line.purchase_line_id.product_id.type == 'product':
                #_logger.info("-> invoice_line.quantity: " + str(invoice_line.quantity))
                #_logger.info("-> invoice_line.purchase_line_id.qty_received: " + str(invoice_line.purchase_line_id.qty_received))
                #_logger.info("-> invoice_line.purchase_line_id.qty_invoiced: " + str(invoice_line.purchase_line_id.qty_invoiced))
#               if invoice_line.quantity <= (invoice_line.purchase_line_id.qty_received - invoice_line.purchase_line_id.qty_invoiced):
#                    raise ValidationError("No se puede postear por la diferencia en las cantidades entregadas de la PO y las cantidades de la factura")
#        raise ValidationError("Test")
#        rec = super(AccountMoveInherit, self).action_post()
        

class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    
    
    @api.onchange('quantity')
    def _onchange_quantity(self):
        if self.quantity:
            _logger.info("-> invoice_line.quantity: " + str(self.quantity))
            _logger.info("-> invoice_line.purchase_line_id.qty_received: " + str(self.purchase_line_id.qty_received))
            _logger.info("-> invoice_line.purchase_line_id.qty_invoiced: " + str(self.purchase_line_id.qty_invoiced))
            if self.purchase_line_id and self.quantity > (self.purchase_line_id.qty_received - self.purchase_line_id.qty_invoiced):
                raise ValidationError("No puede agregar una cantidad mayor a la recibida.")
            #pass