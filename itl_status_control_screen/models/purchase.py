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


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    
    itl_manager_appr_date = fields.Date(string="PO Manager Approval date", compute="_get_po_approval_detail")
    itl_finance_1_appr_date = fields.Date(string="PO Finance 1 Approval date", compute="_get_po_approval_detail")
    itl_finance_2_appr_date = fields.Date(string="PO Finance 2 Approval date", compute="_get_po_approval_detail")
    
    itl_pymnt_rqst_date = fields.Date(string="Payment Req created date", compute="_get_po_payment_detail")
    itl_pymnt_mngr_appr_date = fields.Date(string="Payment Req Manager Apprv date", compute="_get_po_payment_detail")
    itl_pymnt_fin_1_appr_date = fields.Date(string="Payment Req Fin 1 Apprv date", compute="_get_po_payment_detail")
    itl_pymnt_fin_2_appr_date = fields.Date(string="Payment Req Fin 2 Apprv date", compute="_get_po_payment_detail")
    
    itl_inv_payment_state = fields.Selection(
        [('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')], string="Invoice Payment Status", compute="_get_inv_payment_detail")
    itl_inv_pymnt_date = fields.Date(string="Invoice Payment date", compute="_get_inv_payment_detail")
    itl_proof_receipt_date = fields.Date(string="Proof of receipt upload date", compute="_get_proof_receipt_detail")
    
    # Inherit
    def read(self, fields=None, load='_classic_read'):
        self = self.sudo()
        rec = super(PurchaseOrder, self).read(fields, load)
        
        return rec
    
    @api.depends('approval_request_id.approver_ids.status')
    def _get_po_approval_detail(self):
        for purchase in self:
            purchase.itl_manager_appr_date = False
            purchase.itl_finance_1_appr_date = False
            purchase.itl_finance_2_appr_date = False
            if purchase.approval_request_id and len(purchase.approval_request_id.approver_ids) > 0:
                if purchase.approval_request_id.approver_ids[0].status == 'approved':
                    purchase.itl_manager_appr_date = purchase.approval_request_id.approver_ids[0].write_date
                if len(purchase.approval_request_id.approver_ids) > 1 and purchase.approval_request_id.approver_ids[1].status == 'approved':
                    purchase.itl_finance_1_appr_date = purchase.approval_request_id.approver_ids[1].write_date
                if len(purchase.approval_request_id.approver_ids) > 2 and purchase.approval_request_id.approver_ids[2].status == 'approved':
                    purchase.itl_finance_2_appr_date = purchase.approval_request_id.approver_ids[2].write_date
                    
    @api.depends('payment_approval_id.approver_ids.status')
    def _get_po_payment_detail(self):
        for purchase in self:
            purchase.itl_pymnt_rqst_date = False
            purchase.itl_pymnt_mngr_appr_date = False
            purchase.itl_pymnt_fin_1_appr_date = False
            purchase.itl_pymnt_fin_2_appr_date = False
            
            if purchase.payment_approval_id and len(purchase.payment_approval_id.approver_ids) > 0:
                purchase.itl_pymnt_rqst_date = purchase.payment_approval_id.create_date
                
                if purchase.payment_approval_id.approver_ids[0].status == 'approved':
                    purchase.itl_pymnt_mngr_appr_date = purchase.payment_approval_id.approver_ids[0].write_date
                if len(purchase.payment_approval_id.approver_ids) > 1 and purchase.payment_approval_id.approver_ids[1].status == 'approved':
                    purchase.itl_pymnt_fin_1_appr_date = purchase.approval_request_id.approver_ids[1].write_date
                if len(purchase.payment_approval_id.approver_ids) > 2 and purchase.payment_approval_id.approver_ids[2].status == 'approved':
                    purchase.itl_pymnt_fin_2_appr_date = purchase.payment_approval_id.approver_ids[2].write_date
                    
    @api.depends('invoice_ids.invoice_payment_state')
    def _get_inv_payment_detail(self):
        for purchase in self:
            purchase.itl_inv_pymnt_date = False
            purchase.itl_inv_payment_state = False
            if len(purchase.invoice_ids) > 0:
                invoice_ids = purchase.invoice_ids.filtered(lambda i: i.type == 'in_invoice' and i.state == 'posted')
                if len(invoice_ids) > 0:
                    last_invoice_id = purchase.invoice_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    purchase.itl_inv_payment_state = last_invoice_id.invoice_payment_state
                    if last_invoice_id.invoice_payment_state == 'paid':
                        #invoice_payments_widget = json.loads(last_invoice_id.invoice_payments_widget)
                        #if invoice_payments_widget:
                        #    payment_date = invoice_payments_widget['content'][0]['date']
                        #    purchase.itl_inv_pymnt_date = payment_date
                        reconcile_line_ids = last_invoice_id.line_ids._reconciled_lines()
                        aml = self.env['account.move.line'].browse(reconcile_line_ids)
                        payment_ids = aml.mapped('payment_id')
                        if len(payment_ids) > 0:
                            purchase.itl_inv_pymnt_date = payment_ids[0].payment_date
            
            
    @api.depends('message_main_attachment_id')
    def _get_proof_receipt_detail(self):
        for purchase in self:
            purchase.itl_proof_receipt_date = False
            if purchase.message_main_attachment_id:
                purchase.itl_proof_receipt_date = purchase.message_main_attachment_id.create_date