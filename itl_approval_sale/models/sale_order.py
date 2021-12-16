from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError
import math
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #has_changes = fields.Boolean(readonly=True, store=False, compute='_get_invoiced')
    #has_changes = fields.Boolean(readonly=False, store=True)
    # Inherit field
    type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Type",
        compute="_compute_sale_type_id",
        readonly=False,
        store=True,
        track_visibility='onchange'
    )
    
    itl_so_approval = fields.Boolean(compute="_compute_itl_so_approval")
    approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status")
    state = fields.Selection(selection_add=[('refused','Rejected'),('to_approve','To approve'),('approved', 'Approved')])

    @api.depends("company_id")
    def _compute_itl_so_approval(self):
        self.itl_so_approval = self.company_id.itl_so_approval
    
    def send_to_approve(self):
        if not self.env.company.itl_so_approval_category_id:
            raise ValidationError("Approval category is not configured.")

        description = "Líneas de pedido\n"
        prod_vals = {}
        prod_list = []
        for line in self.order_line:
            description += "Producto: "+str(line.product_id.name)+'\t'+"Descripción: "+str(line.name)+'\t'+"Cantidad: "+str(line.product_uom_qty)+'\t'+"Precio unitario: "+str(line.price_unit)+'\t'+"Subtotal: "+str(line.price_subtotal)+'\n'
            prod_vals.update(approval_request_id=self.id)
            prod_vals.update(product_id=line.product_id.id)
            prod_vals.update(description=line.name)
            prod_vals.update(quantity=line.product_uom_qty)
            prod_vals.update(product_uom_id=line.product_uom.id)
            prod_vals.update(product_price=line._get_display_price(line.product_id))
            prod_vals.update(product_doc_price=line.price_unit)
            prod_vals.update(product_discount=line.discount)
            
            prod_list.append((0,0,prod_vals))
            prod_vals = {}

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Venta - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_so_approval_category_id.id,
            'amount': self.amount_total,
            'sale_id': self.id,
            'reason': description
        }

        vals.update(product_line_ids=prod_list)
        self.state = 'to_approve'
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

        self.approval_request_id = rec.id

        self.message_post_with_view('itl_approval_sale.message_approval_sale_created_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)

        rec.message_post_with_view('mail.message_origin_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)
                
    def action_cancel(self):
        rec = super(SaleOrder, self).action_cancel()
        
        if self.approval_request_id and self.approval_request_id.request_status != 'cancel':
            self.approval_request_id.action_cancel()
            self.approval_request_id._get_all_approval_activities().unlink()
            
    def button_refused(self):
        self.state = 'refused'
        if self.approval_request_id:
            self.approval_request_id._get_all_approval_activities().unlink()

    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'refused'])
        return orders.write({
            'state': 'draft',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })
    
    # Inherit method
    """
    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
            
            # Extra code
            ########
            has_changes = False
            for line in order.order_line:
                if line.discount != 0:
                    has_changes = True
                    break
                else:
                    has_changes = False
                price_c = line._get_display_price(line.product_id)
                if price_c != line.price_unit:
                    has_changes = True
                    break
                else:
                    has_changes = False
            order.has_changes = has_changes
            ########
    """
    """
    def _check_if_has_change(self):
        _logger.info("--> _check_if_has_change")
        has_changes = False
        for line in self.order_line:
            if line.discount != 0:
                has_changes = True
                break
            else:
                has_changes = False
            if line.product_id.list_price != 0.0 and line.product_id.list_price != line.price_unit:
                has_changes = True
                break
            else:
                has_changes = False
        self.has_changes = has_changes
    """

    """
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        for line in self:
            if 'params' in self._context and 'id' in self._context['params']:
                sale_id = self.env['sale.order'].browse(self._context['params']['id'])
                sale_id.write({'has_changes': True})
        
    @api.onchange('discount')
    def _onchange_discount(self):
        if self.discount == 0:
            self.order_id.has_changes = False
        else:
            self.order_id.has_changes = True
            
    """