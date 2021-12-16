# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    hide_payment_request_button = fields.Boolean(compute="_hide_payment_request_button")
    has_payment_request = fields.Boolean(compute="_has_payment_request")
    payment_requests_status = fields.Selection([('nothing','No payment request'),
                                                ('all_approved','All approved'),
                                                ('pendings','Pendings'),
                                               ('some_rejeted','Some rejected'),
                                               ('payment_done','Payment Done')], 
                                               compute="_check_payment_requests",
                                              default='nothing')

    payment_approval_id = fields.Many2one('approval.request', string="Payment request", copy = False)
    payment_bill_ids = fields.Many2many('account.move', related='payment_approval_id.bill_ids', string="Related bills in request")
    payment_approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], related="payment_approval_id.request_status", string="Payment request status")
    
    itl_product_type = fields.Selection([('good','Goods'),('service','Service')], string="Product type", copy=False)
    itl_proof_receiving = fields.Binary(string="Proof of receiving", copy=False)
    itl_name_proof_receiving = fields.Char(string="Proof of receiving", copy=False)
    
    itl_urgent_payment = fields.Boolean(string="Urgent payment")
    itl_payment_date = fields.Date(string="Payment date")
    itl_urgency_reason = fields.Text(string="Reason of urgent payment")

    @api.onchange('itl_product_type')
    def _onchange_itl_product_type(self):
        self.itl_proof_receiving = False
        self.itl_name_proof_receiving = False
    
    #@api.depends('invoice_ids')
    def _check_payment_requests(self):
        for purchase in self:
            purchase.payment_requests_status = 'nothing'
            
            if not purchase.payment_approval_id:
                return
            
            if purchase.payment_approval_status == 'approved':
                purchase.payment_requests_status = 'all_approved'
            
            if purchase.payment_approval_status in ['pending', 'new']:
                purchase.payment_requests_status = 'pendings'
                
            if purchase.payment_approval_status in ['refused', 'cancel']:
                purchase.payment_requests_status = 'some_rejeted'
                
            

    @api.depends('invoice_ids')
    def _has_payment_request(self):
        for purchase in self:
            purchase.has_payment_request = False
            for inv in purchase.invoice_ids:
                if inv.approval_request_vendor_bill_id:
                    purchase.has_payment_request = True
        
    
    @api.depends('has_services','has_products')
    def _hide_payment_request_button(self):
        self.hide_payment_request_button = True
        if self.payment_approval_id:
            return
        if self.has_services and self.has_products:
            if self.state in ['purchase','done'] and self.received_products and self.received_products_manual:
                self.hide_payment_request_button = False
        if self.has_services and not self.has_products:
            if self.state in ['purchase','done'] and self.received_products_manual:
                self.hide_payment_request_button = False
        if not self.has_services and self.has_products:
            if self.state in ['purchase','done'] and self.received_products:
                self.hide_payment_request_button = False       
            
    
    approval_request_vendor_bill_id = fields.Many2one('approval.request', string="Payment approval", readonly=True, store=True, copy=False)
    approval_vendor_bill_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], related="approval_request_vendor_bill_id.request_status", string="Payment approval status")
    
    def payment_request_approval(self):
        #if not self.itl_product_type:
        #    raise ValidationError("Please, select if Product type is Goods or Service.")
        #if self.itl_product_type == 'good' and not self.itl_proof_receiving:
        #    raise ValidationError("You need to upload a picture of the goods.")
        # TODO (jovani.martinez): This was having problems so we decided to comment this lines out
        #if self.create_date.date() == fields.Date.today():
        #    raise ValidationError("You can not do a payment request in the same day the purchase order was created.")
        view = self.env.ref('itl_approval_vendor_bill.payment_request_form_purchase')
        view_id = view and view.id or False
        context = dict(self._context or {})
        return {
            'name': 'Payment Request',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.payment.request',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
    
    def send_to_approve_request_payment(self):
        if not self.env.company.itl_vendor_payment_approval_category_id:
            raise ValidationError("Approval category is not configured.")
        
        description = "Líneas de compra\n"
        prod_vals = {}
        prod_list = []
        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Payment bill - ' + str(self.name),
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_vendor_payment_approval_category_id.id,
            'amount': self.amount_total,
            #'bill_id': self.id,
            'payment_purchase_id': self.id,
            'reason': description,
            'itl_urgent_payment': self.itl_urgent_payment,
            'itl_payment_date': self.itl_payment_date,
            'itl_urgency_reason': self.itl_urgency_reason
        }

        if not self.payment_approval_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.payment_approval_id
            for p in rec.product_line_ids:
                p.unlink()
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()
            
        for line in self.order_line:
            description += "Producto: "+str(line.product_id.name)+'\t'+"Descripción: "+str(line.name)+'\t'+"Cantidad: "+str(line.product_uom_qty)+'\t'+"Precio unitario: "+str(line.price_unit)+'\t'+"Subtotal: "+str(line.price_subtotal)+'\n'
            prod_vals.update(approval_request_id=rec.id)
            prod_vals.update(product_id=line.product_id.id)
            prod_vals.update(description=line.name)
            prod_vals.update(quantity=line.product_uom_qty)
            prod_vals.update(product_uom_id=line.product_uom.id)
            #prod_vals.update(product_price=line._get_display_price(line.product_id))
            prod_vals.update(product_doc_price=line.price_unit)
            #prod_vals.update(product_discount=line.discount)
            
            prod_list.append((0,0,prod_vals))
            prod_vals = {}
        
        rec.product_line_ids = prod_list
        
        self.payment_approval_id = rec.id