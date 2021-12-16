from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    #itl_purchase_id = fields.Many2one('purchase.order', copy=False)
    #approval_vendor_bill_status = fields.Selection([
    #    ('new', 'To Submit'),
    #    ('pending', 'Submitted'),
    #    ('approved', 'Approved'),
    #    ('refused', 'Rejected'),
    #    ('cancel', 'Cancel')], related='itl_purchase_id.approval_vendor_bill_status')
    
    
    def action_post_itl_approval_vendor_bill(self):
        self.action_post()
        
    approval_request_vendor_bill_id = fields.Many2one('approval.request', string="Payment approval", readonly=False, store=True, copy=False)
    approval_vendor_bill_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], related="approval_request_vendor_bill_id.request_status", string="Payment approval status")
    
    def send_to_approve_request(self, purchase_id):
        if not self.env.company.itl_vendor_payment_approval_category_id:
            raise ValidationError("Approval category is not configured.")
        if len(self.invoice_line_ids) == 0:
            raise ValidationError("Faltan líneas de producto en la factura.")
        description = "Líneas de factura\n"
        prod_vals = {}
        prod_list = []
        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Payment bill - ' + str(self.id),
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_vendor_payment_approval_category_id.id,
            'amount': self.amount_total,
            'bill_id': self.id,
            'purchase_id': purchase_id.id,
            'reason': description
        }

        #vals.update(product_line_ids=prod_list)
        
        if not self.approval_request_vendor_bill_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.approval_request_vendor_bill_id
            for p in rec.product_line_ids:
                p.unlink()
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()
            
        for line in self.invoice_line_ids:
            description += "Producto: "+str(line.product_id.name)+'\t'+"Descripción: "+str(line.name)+'\t'+"Cantidad: "+str(line.quantity)+'\t'+"Precio unitario: "+str(line.price_unit)+'\t'+"Subtotal: "+str(line.price_subtotal)+'\n'
            prod_vals.update(approval_request_id=rec.id)
            prod_vals.update(product_id=line.product_id.id)
            prod_vals.update(description=line.name)
            prod_vals.update(quantity=line.quantity)
            prod_vals.update(product_uom_id=line.product_uom_id.id)
            #prod_vals.update(product_price=line._get_display_price(line.product_id))
            prod_vals.update(product_doc_price=line.price_unit)
            #prod_vals.update(product_discount=line.discount)
            
            prod_list.append((0,0,prod_vals))
            prod_vals = {}
        
        rec.product_line_ids = prod_list

        self.approval_request_vendor_bill_id = rec.id
