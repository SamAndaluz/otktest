# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
import json

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    
    itl_total_quantity = fields.Float(string="Quantity", compute="_get_total_quantity")
    itl_approval_date = fields.Date(string="Approval Date", compute="_get_approval_detail")
    itl_delivery_create_date = fields.Date(string="Delivery Created Date", compute="_get_delivery_details")
    itl_delivery_by = fields.Selection(
        [('logistic_company','Logistic company'),
         ('employee','Employee'),
         ('collected_employee','Collected by employee')], string="Delivery by", compute="_get_delivery_details")
    itl_shipping_date = fields.Date(string="Delivery Shipping Date", compute="_get_delivery_details")
    itl_effective_delivery_date = fields.Date(string="Customer Receiving Date", compute="_get_delivery_details")
    itl_proof_deliver_date = fields.Date(string="Proof of delivery upload date", compute="_get_delivery_details")
    itl_customer_payment_status = fields.Selection(
        [('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')], string="Payment Status", compute="_get_payment_details")
    itl_customer_payment_date = fields.Date(string="Payment Date", compute="_get_payment_details")
    itl_overdue_days = fields.Integer(string="Overdue Days", compute="_get_payment_details")
    
    # Inherit
    def read(self, fields=None, load='_classic_read'):
        self = self.sudo()
        #self._get_overdue_payment_details()
        rec = super(SaleOrder, self).read(fields, load)
        
        return rec
    
    @api.depends('order_line.product_uom_qty')
    def _get_total_quantity(self):
        for sale in self:
            sale.itl_total_quantity = sum(sale.order_line.mapped('product_uom_qty'))
            
    @api.depends('approval_request_id.request_status')
    def _get_approval_detail(self):
        for sale in self:
            sale.itl_approval_date = False
            if sale.approval_request_id.request_status == 'approved':
                if len(sale.approval_request_id.approver_ids) > 0:
                    sale.itl_approval_date = sale.approval_request_id.approver_ids[-1].write_date
                
    @api.depends('picking_ids.state')
    def _get_delivery_details(self):
        for sale in self:
            sale.itl_delivery_create_date = False
            sale.itl_shipping_date = False
            sale.itl_effective_delivery_date = False
            sale.itl_proof_deliver_date = False
            sale.itl_delivery_by = False
            if len(sale.picking_ids) > 0:
                delivery_ids = sale.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')
                if len(delivery_ids) > 0:
                    last_delivery_id = delivery_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    sale.itl_delivery_create_date = last_delivery_id.create_date
                    sale.itl_shipping_date = last_delivery_id.itl_pickup_date
                    sale.itl_effective_delivery_date = last_delivery_id.itl_delivery_date
                    sale.itl_proof_deliver_date = last_delivery_id.message_main_attachment_id.create_date
                    sale.itl_delivery_by = last_delivery_id.itl_delivery_by
                    
            if sale.signature:
                sale.itl_effective_delivery_date = sale.signed_on
                sale.itl_proof_deliver_date = sale.signed_on
                
    @api.depends('invoice_ids.invoice_payment_state')
    def _get_payment_details(self):
        for sale in self:
            sale.itl_customer_payment_status = False
            sale.itl_customer_payment_date = False
            sale.itl_overdue_days = False
            if len(sale.invoice_ids) > 0:
                invoice_ids = sale.invoice_ids.filtered(lambda i: i.type == 'out_invoice' and i.state == 'posted')
                if len(invoice_ids) > 0:
                    last_invoice_id = invoice_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    sale.itl_customer_payment_status = last_invoice_id.invoice_payment_state
                    if last_invoice_id.invoice_payment_state == 'paid':
                        reconcile_line_ids = last_invoice_id.line_ids._reconciled_lines()
                        aml = self.env['account.move.line'].browse(reconcile_line_ids)
                        payment_ids = aml.mapped('payment_id')
                        if len(payment_ids) > 0:
                            sale.itl_customer_payment_date = payment_ids[0].payment_date
                    if not sale.itl_customer_payment_date:
                        delta = fields.Datetime.now() - last_invoice_id.create_date
                        sale.itl_overdue_days = delta.days
    
    
    def _get_overdue_payment_details(self):
        for sale in self:
            itl_customer_payment_date = False
            sale.itl_overdue_days = 0
            if len(sale.invoice_ids) > 0:
                invoice_ids = sale.invoice_ids.filtered(lambda i: i.type == 'out_invoice' and i.state == 'posted')
                if len(invoice_ids) > 0:
                    last_invoice_id = invoice_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    if last_invoice_id.invoice_payment_state == 'paid':
                        reconcile_line_ids = last_invoice_id.line_ids._reconciled_lines()
                        if reconcile_line_ids:
                            aml = self.env['account.move.line'].browse(reconcile_line_ids)
                            payment_ids = aml.mapped('payment_id')
                            if len(payment_ids) > 0:
                                itl_customer_payment_date = payment_ids[0].payment_date
                    if not itl_customer_payment_date:
                        delta = fields.Datetime.now() - last_invoice_id.create_date
                        sale.itl_overdue_days = delta.days