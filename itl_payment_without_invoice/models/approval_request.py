from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import re

import logging
_logger = logging.getLogger(__name__)


class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    itl_payment_control_id = fields.Many2one('itl.payment.control', copy=False, string="Payment control", ondelete="cascade")
    
    itl_document_type = fields.Selection([('pediment','Pedimento'),('foreing_invoice','Foreing invoice')], string="Document type", related="itl_payment_control_id.itl_document_type")
    itl_foreing_invoice = fields.Char(string="Foreing invoice number", related="itl_payment_control_id.itl_foreing_invoice")
    itl_pediment = fields.Char(help='Optional field for entering the customs information in the case '
        'of first-hand sales of imported goods or in the case of foreign trade'
        ' operations with goods or services.\n'
        'The format must be:\n'
        ' - 2 digits of the year of validation followed by two spaces.\n'
        ' - 2 digits of customs clearance followed by two spaces.\n'
        ' - 4 digits of the serial number followed by two spaces.\n'
        ' - 1 digit corresponding to the last digit of the current year, '
        'except in case of a consolidated customs initiated in the previous '
        'year of the original request for a rectification.\n'
        ' - 6 digits of the progressive numbering of the custom.',
        string='Pedimento', size=21, related="itl_payment_control_id.itl_pediment")
    
    #Inherit method
    def action_approve(self, approver=None):
        if self.itl_payment_control_id:
            self = self.with_context(payment_wo_invoice=True)
        super(ApprovalRequestCustom, self).action_approve()
        
        approvals = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'approved')
        if len(approvals) == len(self.mapped('approver_ids')):
            if self.category_id.code == 'PAYMENT':
                self.payment_purchase_id.action_register_payment()
                
    