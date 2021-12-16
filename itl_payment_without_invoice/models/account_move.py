from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    itl_is_payment_wo_invoice = fields.Boolean(string="Payment w/o invoice", copy=False)
    itl_payment_control_id = fields.Many2one('itl.payment.control', string="Payment control", copy=False)
    itl_payment_control_done = fields.Boolean(related='itl_payment_control_id.itl_is_done', string="Payment control done")
    itl_is_advance_payment = fields.Boolean(string="Is advance payment", copy=False)
    
    itl_purchase_id = fields.Many2one('purchase.order', related='itl_payment_control_id.itl_purchase_id', string="Purchase Order", copy=False)
    itl_advance_bill_id = fields.Many2one('account.move', related='itl_payment_control_id.itl_advance_bill_id', string="Down payment Bill", copy=False)
    
    @api.onchange('itl_is_payment_wo_invoice')
    def _onchange_itl_is_payment_wo_invoice(self):
        self.itl_payment_control_id = False
        
        
    def itl_payment_control(self):
        if not self.itl_payment_control_id.itl_advance_bill_id:
            raise ValidationError("The payment control related has not a down payment bill.")
        if self.itl_payment_control_id.itl_advance_bill_id.invoice_payment_state == 'not_paid':
            raise ValidationError("The related down payment invoice is not paid.")
        if self.itl_payment_control_id.itl_is_done:
            raise ValidationError("The related payment control was completed, try to use another one.")
            
        itl_advance_bill_id = self.itl_payment_control_id.itl_advance_bill_id
        
        # Get Advance payment from Down paymnet bill
        payment_id = self.env['account.payment'].search([('invoice_ids.id','=',itl_advance_bill_id.id)])
        payment_info = itl_advance_bill_id._get_payments_reconciled_info()
        dict_payment_id = payment_info['content'][0]['payment_id']
        move_id = payment_info['content'][0]['move_id']
        move_id = self.env['account.move'].browse(move_id)
        move_line = self.env['account.move.line'].browse(dict_payment_id)
        # Remove the payment from bill
        move_line.with_context({'move_id': itl_advance_bill_id.id}).remove_move_reconcile()
        
        # Create reverse move (Refund)
        vals = {'move_id': itl_advance_bill_id.id,
               'refund_method': 'refund',
               'reason': ''}
        amr = self.env['account.move.reversal'].with_context(active_ids=itl_advance_bill_id.id, active_model='account.move').create(vals)
        amr._compute_from_moves()
        # Create the reverse move and post it
        rev_invoice_id = amr.itl_reverse_moves()
        rev_invoice_id.action_post()
        # Try to reconcile the payment with the new invoice
        to_reconcile = itl_advance_bill_id._get_payments_widget_to_reconcile_info()
        m_lines = itl_advance_bill_id._get_reversal_move_line()
        ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [rev_invoice_id.id, move_id.id])
        for ml in ml_to_add:
            itl_advance_bill_id.js_assign_outstanding_line(ml.id)

        rme_lines = itl_advance_bill_id._get_reversal_move_line()
        rme_lines_to_add = rme_lines.filtered(lambda i: i.move_id.id in [move_id.id])
        for rme_ml in rme_lines_to_add:
            self.js_assign_outstanding_line(rme_ml.id)
                            
        self.itl_payment_control_id.itl_bill_id = self
        self.itl_payment_control_id.itl_is_done = True
        self.invoice_origin = self.itl_payment_control_id.itl_purchase_id.name
        
        _logger.info("-----==> rev_invoice_id: " + str(rev_invoice_id))
        
        #raise ValidationError("TESTING++++++")