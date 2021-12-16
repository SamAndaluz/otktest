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
    
    has_approval_group = fields.Boolean(compute="_check_if_has_group")
    approval_request_id = fields.Many2one('approval.request', string="Purchase approval", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status", string="Purchase approval status")
    state = fields.Selection(selection_add=[('refused','Rejected')])
    
    @api.depends()
    def _check_if_has_group(self):
        if self.env.user.has_group('itl_approval_purchase.group_confirm_po'):
            self.has_approval_group = True
        else:
            self.has_approval_group = False
    
    def send_to_approve(self):
        if not self.env.company.po_approval_category_id:
            raise ValidationError("Approval category is not configured.")
        if len(self.order_line) == 0:
            raise ValidationError("Faltan líneas de producto en la orden de compra.")
        description = "Líneas de pedido\n"
        prod_vals = {}
        prod_list = []

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Compra - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.po_approval_category_id.id,
            'amount': self.amount_total,
            'purchase_id': self.id,
            'reason': description
        }

        #vals.update(product_line_ids=prod_list)
        
        if not self.approval_request_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.approval_request_id
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

        self.approval_request_id = rec.id

        self.state = 'to approve'

        self.message_post_with_view('itl_approval_purchase.message_approval_created_link',
                        values={'self': rec, 'origin': self},
                        subtype_id=self.env.ref('mail.mt_note').id)

        rec.message_post_with_view('mail.message_origin_link',
                        values={'self': rec, 'origin': self},
                        subtype_id=self.env.ref('mail.mt_note').id)
            
    def button_cancel(self):
        rec = super(PurchaseOrder, self).button_cancel()
        _logger.info("---# req_status: " + str(self.approval_request_id.request_status))
        if self.approval_request_id and self.approval_request_id.request_status != 'cancel':
            self.approval_request_id.action_cancel()
            self.approval_request_id._get_all_approval_activities().unlink()
    
    def button_refused(self):
        self.state = 'refused'
        if self.approval_request_id:
            self.approval_request_id._get_all_approval_activities().unlink()