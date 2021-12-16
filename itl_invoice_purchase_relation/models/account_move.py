from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    itl_purchase_related = fields.Boolean(string="Has purchase order related", copy=False, compute="_has_purchase_related")
    
    def _has_purchase_related(self):
        purchase_id = self.line_ids.mapped('purchase_line_id.order_id')
        if purchase_id:
            self.itl_purchase_related = True
        else:
            self.itl_purchase_related = False
    """
    def unlink_bill(self):
        if self.approval_request_vendor_bill_id:
            purchase_id = self.approval_request_vendor_bill_id.purchase_id
        else:
            purchase_id = self.line_ids.mapped('purchase_line_id.order_id')
        invoice_lines = []
        for inv_line in self.invoice_line_ids:
            invoice_lines.append((3, inv_line.id))
        purchase_id.order_line.invoice_lines = invoice_lines
        purchase_id.invoice_ids = [(3, self.id)]
        self.invoice_origin = False
        #self.approval_request_vendor_bill_id.action_cancel()
    """
    
    def unlink_bill(self):
        if self.approval_request_vendor_bill_id:
            purchase_id = self.approval_request_vendor_bill_id.payment_purchase_id
        else:
            purchase_id = self.line_ids.mapped('purchase_line_id.order_id')
        invoice_lines = []
        for inv_line in self.invoice_line_ids:
            invoice_lines.append((3, inv_line.id))
        purchase_id.order_line.invoice_lines = invoice_lines
        purchase_id.invoice_ids = [(3, self.id)]
        if self.invoice_origin:
            lst_origin = str(self.invoice_origin).split(',')
            lst_origin.remove(purchase_id.name)
            lst_origin.sort(reverse=False)
            origin = ",".join(lst_origin)
            self.invoice_origin = origin
        
    def get_invoice_details(self):
        for invoice in self:
            if not invoice.invoice_origin:
                purchase_ids = invoice.line_ids.mapped('purchase_line_id.order_id.name')
                _logger.info("---> purchase_ids: " + str(purchase_ids))
                if purchase_ids:
                    purchase_ids.sort(reverse=False)
                    origin = ",".join(purchase_ids)
                    invoice.invoice_origin = origin
        