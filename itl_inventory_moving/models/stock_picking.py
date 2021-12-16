# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"
    
    
    itl_logistic_company_id = fields.Many2one('res.partner', string="Logistic company")
    itl_logistic_company_email = fields.Char(related="itl_logistic_company_id.email", string="Logistic company email")
    #itl_employee_id = fields.Many2one('hr.employee', string="Delivery employee")
    itl_employee_partner_id = fields.Many2one('res.partner', string="Employee contact")
    itl_employee_email = fields.Char(related="itl_employee_partner_id.email", string="Employee email")
    itl_purchase_id = fields.Many2one('purchase.order', string="Purchase order")
    itl_origin_sale = fields.Char(string="Original SO number")
    
    itl_location_id = fields.Many2one(
        'stock.location', "Source Location:",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=True, readonly=True, required=False,
        states={'draft': [('readonly', False)]})
    itl_warehouse_id = fields.Many2one('stock.warehouse', string="Source Warehouse", compute="_get_warehouse")
    itl_address_origin_id = fields.Many2one('res.partner', string="Source Address", compute="_get_address")
    itl_source_contact_id = fields.Many2one('res.partner', string="Source Contact")
    #itl_warehouse_contact_child_ids = fields.One2many(related="itl_address_origin_id.child_ids")
    itl_origin_email = fields.Char(related="itl_source_contact_id.email", string="Source email")
    
    itl_location_warehouse_id = fields.Many2one('stock.warehouse', string="Source Warehouse", compute="_get_warehouse")
    itl_address_warehouse_id = fields.Many2one('res.partner', string="Source Address", compute="_get_address")
    itl_origin_contact_id = fields.Many2one('res.partner', string="Source Contact", compute="_get_contact")
    #itl_address_warehouse_child_ids = fields.One2many(related="itl_address_warehouse_id.child_ids")
    itl_email_warehouse = fields.Char(related="itl_address_warehouse_id.email")
    
    itl_location_dest_id = fields.Many2one(
        'stock.location', "Destination Location:",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=True, readonly=True, required=False,
        states={'draft': [('readonly', False)]})
    itl_warehouse_dest_id = fields.Many2one('stock.warehouse', string="Destination Warehouse", compute="_get_warehouse")
    itl_address_dest_id = fields.Many2one('res.partner', string="Destination Address", compute="_get_address")
    itl_dest_contact_id = fields.Many2one('res.partner', string="Destination Contact")
    #itl_warehouse_dest_contact_child_ids = fields.One2many(related="itl_address_dest_id.child_ids")
    itl_dest_email = fields.Char(related="itl_dest_contact_id.email", string="Destination email")
    
    itl_transfer_origin = fields.Boolean()
    itl_driver_name = fields.Char(string="Driver's name")
    itl_type_of_car = fields.Char(string="Type of car")
    itl_plate_of_car = fields.Char(string="Plate of car")
    itl_delivery_by = fields.Selection([('logistic_company','Logistic company'),('employee','Employee'),('collected_employee','Collected by employee')], string="Delivery by")
    itl_pickup_date = fields.Datetime('Pickup Date', store=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    itl_delivery_date = fields.Datetime('Delivery Date', store=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    itl_is_return = fields.Boolean(string="Is return", readonly=True)
    itl_sequence_code = fields.Char(related="picking_type_id.sequence_code")
    itl_exchange_receipt_id = fields.Many2one('stock.picking', string="Exchange receipt")
    itl_transfer_picking_id = fields.Many2one('stock.picking', string="Transfer picking")
    itl_is_rme = fields.Boolean(related="sale_id.itl_is_rme")
    itl_hide_send_to_approve = fields.Boolean(compute="check_if_hide_send_to_approve_button")
    itl_first_review = fields.Boolean(string="First review")
    itl_first_date_review = fields.Datetime(string="First date review")
    # Inherit
    state = fields.Selection(selection_add=[('to_approve','To approve'),('approved', 'Approved'),('refused','Rejected')])
    #
    
    itl_approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    itl_approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="itl_approval_request_id.request_status")    
    
    @api.depends('itl_location_warehouse_id','itl_warehouse_id','itl_warehouse_dest_id')
    def _get_contact(self):
        for picking in self:
            picking.itl_origin_contact_id = False
            if picking.itl_location_warehouse_id:
                warehouse_contact = picking.itl_location_warehouse_id.itl_encargado
                if len(warehouse_contact) > 0:
                    picking.itl_origin_contact_id = warehouse_contact[0]
            if picking.itl_warehouse_id:
                warehouse_contact = picking.itl_warehouse_id.itl_encargado
                if len(warehouse_contact) > 0:
                    picking.itl_source_contact_id = warehouse_contact[0]
            if picking.itl_warehouse_dest_id:
                warehouse_contact = picking.itl_warehouse_dest_id.itl_encargado
                if len(warehouse_contact) > 0:
                    picking.itl_dest_contact_id = warehouse_contact[0]
        
    def check_if_hide_send_to_approve_button(self):
        self.itl_hide_send_to_approve = False
        if self.state not in ['draft','waiting','confirmed','assigned'] or self.itl_transfer_origin or self.itl_sequence_code == 'PICK' or (self.picking_type_code in ['outgoing'] and self.itl_is_return) or (self.picking_type_code in ['incoming','internal'] and self.itl_approval_request_id.id) or (self.picking_type_code in ['incoming'] and not self.itl_is_return) or (not self.itl_is_return and self.sale_id and self.sale_id.approval_status == 'approved'):
            self.itl_hide_send_to_approve = True
    
    @api.onchange('itl_location_id','itl_location_dest_id')
    def _get_address(self):
        for picking in self:
            picking.itl_address_origin_id = False
            picking.itl_address_dest_id = False
            picking.itl_address_warehouse_id = False
            if picking.picking_type_code in ['internal']:
                if picking.itl_location_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',picking.itl_location_id.id)])
                    picking.itl_address_origin_id = warehouse_origin_id.partner_id
                if picking.itl_location_dest_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.itl_location_dest_id.id),('wh_output_stock_loc_id','=',picking.itl_location_dest_id.id)])
                    picking.itl_address_dest_id = warehouse_origin_id.partner_id
            if picking.picking_type_code in ['outgoing']:
                if picking.location_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.location_id.id),('wh_output_stock_loc_id','=',picking.location_id.id)])
                    picking.itl_address_warehouse_id = warehouse_origin_id.partner_id
            if picking.picking_type_code in ['incoming']:
                if picking.location_dest_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.location_dest_id.id),('wh_output_stock_loc_id','=',picking.location_dest_id.id)])
                    picking.itl_address_warehouse_id = warehouse_origin_id.partner_id
                
    @api.onchange('itl_location_id','itl_location_dest_id','location_id','location_dest_id')
    def _get_warehouse(self):
        for picking in self:
            picking.itl_warehouse_id = False
            picking.itl_warehouse_dest_id = False
            picking.itl_location_warehouse_id = False
            if picking.picking_type_code in ['internal']:
                if picking.itl_location_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',picking.itl_location_id.id)])
                    picking.itl_warehouse_id = warehouse_origin_id
                if picking.itl_location_dest_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.itl_location_dest_id.id),('wh_output_stock_loc_id','=',picking.itl_location_dest_id.id)])
                    picking.itl_warehouse_dest_id = warehouse_origin_id
            if picking.picking_type_code in ['outgoing']:
                if picking.location_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.location_id.id),('wh_output_stock_loc_id','=',picking.location_id.id)])
                    picking.itl_location_warehouse_id = warehouse_origin_id
            if picking.picking_type_code in ['incoming']:
                if picking.location_dest_id:
                    warehouse_origin_id = self.env['stock.warehouse'].sudo().search(['|',('lot_stock_id','=',picking.location_dest_id.id),('wh_output_stock_loc_id','=',picking.location_dest_id.id)])
                    picking.itl_location_warehouse_id = warehouse_origin_id
    
    # Inherit
    @api.onchange('picking_type_id', 'partner_id','itl_location_dest_id')
    def onchange_picking_type(self):
        super(Picking, self).onchange_picking_type()
        if self.picking_type_code == 'internal' and self.itl_location_dest_id and not 'Output' in self.itl_location_dest_id.name:
            if self.env.company.itl_location_dest_id:
                self.location_dest_id = self.env.company.itl_location_dest_id
        elif self.itl_location_dest_id:
            self.location_dest_id = self.itl_location_dest_id
        if self.itl_is_return:
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            self.location_id = customerloc
    
    @api.depends('state', 'is_locked')
    def _compute_show_validate(self):
        for picking in self:
            picking.show_validate = True
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned','approved') or not picking.is_locked:
                picking.show_validate = False
            elif not self.id:
                picking.show_validate = False
                
    
    def _check_if_hide_validate_button1(self):
        super(Picking, self)._check_if_hide_validate_button1()
        self.itl_hide_validate_button1 = True
        if self.picking_type_code in ['internal']:
            if (self.itl_approval_request_id and self.itl_approval_status in ('approved') and self.state != 'done') or (self.itl_transfer_origin and self.state != 'done') or (self.itl_sequence_code == 'PICK' and self.state != 'done'):
                self.itl_hide_validate_button1 = False
        if self.picking_type_code in ['outgoing']:
            self.itl_hide_validate_button1 = False
            if self.state not in ('draft', 'waiting', 'confirmed', 'assigned','approved'):
                self.itl_hide_validate_button1 = True
        if self.picking_type_code in ['incoming'] and self.itl_is_return:
            self.itl_hide_validate_button1 = False
            if not self.itl_approval_request_id or self.itl_approval_status not in ('approved') or self.state == 'done':
                self.itl_hide_validate_button1 = True
        if self.picking_type_code in ['incoming'] and not self.itl_is_return:
            self.itl_hide_validate_button1 = False
            if self.partner_id.itl_create_journal_in_receipt:
                if self.state in ['waiting','confirmed'] or not self.show_validate or not self.itl_journal_entry_id or not self.itl_reversal_journal_entry_id:
                    self.itl_hide_validate_button1 = True
            else:
                if self.state in ['waiting','confirmed'] or not self.show_validate:
                    self.itl_hide_validate_button1 = True
        
    def _check_if_hide_validate_button2(self):
        super(Picking, self)._check_if_hide_validate_button2()
        self.itl_hide_validate_button2 = False
        if self.picking_type_code in ['internal']:
            if self.state not in ('draft', 'waiting', 'confirmed', 'assigned','approved') or not self.show_validate:
                self.itl_hide_validate_button2 = True
        if self.picking_type_code in ['outgoing']:
            if not self.itl_approval_request_id or self.itl_approval_status not in ('approved') or self.state == 'done':
                self.itl_hide_validate_button2 = True
    
    def send_to_approve(self):
        if not self.env.company.itl_transfer_approval_category_id:
            raise ValidationError("Approval category is not configured.")
            
        if len(self.move_line_ids_without_package) == 0:
            raise ValidationError('Debe agregar líneas de producto en la pestaña "Operaciones detalladas".')
        #self.email_validations()

        description = "Líneas de pedido\n"
        prod_vals = {}
        prod_list = []
        for line in self.move_line_ids_without_package:
            prod_vals.update(approval_request_id=self.id)
            prod_vals.update(product_id=line.product_id.id)
            prod_vals.update(description=line.product_id.display_name)
            prod_vals.update(quantity=line.qty_done)
            prod_vals.update(lot_id=line.lot_id.id)
            prod_vals.update(product_uom_id=line.product_uom_id.id)
            
            prod_list.append((0,0,prod_vals))
            prod_vals = {}

        approval_obj = self.env['approval.request']
        
        type = False
        if self.picking_type_code == 'outgoing':
            type = 'Delivery'
        if self.picking_type_code == 'internal':
            type = 'Transfer'
        if self.itl_is_return:
            type = 'Return'
        
        vals = {
            'name': type + ' - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_transfer_approval_category_id.id,
            'stock_picking_id': self.id
        }

        vals.update(product_line_ids=prod_list)
        self.state = 'to_approve'
        if not self.itl_approval_request_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.itl_approval_request_id
            for p in rec.product_line_ids:
                p.unlink()
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()

        self.itl_approval_request_id = rec.id

        self.message_post_with_view('itl_inventory_moving.message_approval_transfer_created_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)

        rec.message_post_with_view('mail.message_origin_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)
        
    def button_refused(self):
        self.state = 'refused'
        if self.itl_approval_request_id:
            self.itl_approval_request_id._get_all_approval_activities().unlink()
    
    # Inherit
    def button_validate(self):
        self = self.sudo()
        pickings_start = self.env['stock.picking'].search([])
        rec = super(Picking, self).button_validate()
        
        if self.picking_type_code in ['internal'] and not self.sale_id.itl_is_rme and self.itl_warehouse_id != self.itl_warehouse_dest_id:
            if not self.itl_transfer_origin:
                picking_obj = self.env['stock.picking']
                warehouse_dest_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',self.itl_location_dest_id.id)])
                
                lines = []
                for line in self.move_line_ids_without_package:
                    line_vals = {}
                    line_vals['product_id'] = line.product_id.id
                    line_vals['location_id'] = self.location_dest_id.id
                    line_vals['location_dest_id'] = self.itl_location_dest_id.id
                    line_vals['lot_id'] = line.lot_id.id
                    line_vals['qty_done'] = line.qty_done
                    line_vals['product_uom_id'] = line.product_uom_id.id

                    lines.append((0, 0, line_vals))
                _logger.info("###>>>> lines: " + str(lines))
                picking_vals = {'picking_type_id': warehouse_dest_id.int_type_id.id,
                               'location_id': self.location_dest_id.id,
                               'location_dest_id': self.itl_location_dest_id.id,
                               'itl_location_id': self.itl_location_id.id,
                               'itl_location_dest_id': self.itl_location_dest_id.id,
                                'itl_transfer_origin': True,
                                'scheduled_date': self.scheduled_date,
                                'origin': self.origin,
                                'itl_logistic_company_id': self.itl_logistic_company_id.id or False,
                                'itl_employee_partner_id': self.itl_employee_partner_id.id or False,
                                'itl_driver_name': self.itl_driver_name,
                                'itl_type_of_car': self.itl_type_of_car,
                                'itl_plate_of_car': self.itl_plate_of_car,
                                'immediate_transfer': True,
                                'origin': self.name,
                                'itl_pickup_date': self.itl_pickup_date,
                                'itl_delivery_date': self.itl_delivery_date,
                                'itl_delivery_by': self.itl_delivery_by,
                                'itl_source_contact_id': self.itl_source_contact_id.id or False,
                                'itl_dest_contact_id': self.itl_dest_contact_id.id or False,
                                'move_line_ids_without_package': lines
                               }
                
                new_picking = picking_obj.sudo().create(picking_vals)
                
                new_picking.state = 'assigned'
                
                for ml in new_picking.move_line_ids_without_package:
                    if ml.lot_id:
                        ml.lot_id._compute_location_ids()
                self.itl_transfer_picking_id = new_picking
                
                new_picking.itl_transfer_picking_id = self.id
                
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                base_url += '/web#id=%d&view_type=form&model=%s' % (new_picking.id, self._name)
                if self.itl_dest_contact_id and self.itl_dest_contact_id.email:
                    self.send_receiving_email(base_url, new_picking)
                
        if self.itl_is_return:
            if self.sale_id:
                if self.sale_id.invoice_count != 0:
                    invoice_id = self.sale_id.invoice_ids[0]
                    
                    vals = {'move_id': invoice_id.id,
                           'refund_method': 'cancel'}
                    amr = self.env['account.move.reversal'].with_context(active_ids=invoice_id.id, active_model='account.move').create(vals)
                    amr._compute_from_moves()
                    rev_invoice_id = amr.itl_reverse_moves()
                    msg = _("La factura %s fue cancelada con la factura rectificativa %s.") % (invoice_id.name, rev_invoice_id.name)
                    self.message_post(body=msg)
                    
                    payment_id = self.env['account.payment'].search([('invoice_ids.id','=',invoice_id.id)])
                    if payment_id:
                        payment_id.action_draft()
                        #payment_id.cancel()
                        msg = _("El pago %s de la factura %s fue cancelado.") % (payment_id.name, invoice_id.name)
                        self.message_post(body=msg)
        if self.picking_type_code in ['outgoing'] and self.sale_id.itl_is_rme:
            picking_type_id = self.env['stock.picking.type'].search([('warehouse_id','=',self.sale_id.itl_warehouse_return_id.id),('code','=','incoming')])
            
            defaults = {'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                       'picking_type_id': picking_type_id.id}
            vals = {
                'partner_id': self.partner_id.id,
                'picking_type_id': picking_type_id.id,
                'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                'immediate_transfer': True,
                'origin': self.origin,
                'sale_id': self.sale_id.id
            }
            lines = []
            origin_picking = self.sale_id.itl_sale_origin_id.picking_ids.filtered(lambda i: i.picking_type_code == 'outgoing')
            lot_id = False
            if origin_picking and origin_picking[0].move_line_ids_without_package:
                lot_id = origin_picking[0].move_line_ids_without_package[0].lot_id.id
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            for line in self.move_line_ids_without_package:
                val_line = {
                    'product_id': line.product_id.id,
                    'location_id': customerloc.id,
                    'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                    'qty_done': line.qty_done,
                    'product_uom_id': line.product_uom_id.id,
                    'lot_id': lot_id
                }
                lines.append((0, 0, val_line))
                #n_line = line.copy(default={'picking_id': new_recepit.id})
            
            vals.update(move_line_ids_without_package=lines)
            #new_recepit = self.copy(default=defaults)
            #new_recepit.immediate_transfer = True
            new_recepit = self.env['stock.picking'].create(vals)
            new_recepit.location_id = customerloc
            self.itl_exchange_receipt_id = new_recepit
            
            
            self.print_invoice(with_return=False)
            
        if self.picking_type_code in ['incoming'] and self.sale_id.itl_is_rme:
            sale_id = self.sale_id
            if not self.sale_id:
                sale_id = self.env['sale.order'].search([('name','=',self.origin)], limit=1)
            if not sale_id:
                raise ValidationError("No se encontró la orden de venta relacionada.")
            if len(sale_id.itl_sale_origin_id.invoice_ids) != 0:
                invoice_id = sale_id.itl_sale_origin_id.invoice_ids[0]
                invoice_payment_state = invoice_id.invoice_payment_state
                if invoice_payment_state == 'paid':
                    payment_id = self.env['account.payment'].search([('invoice_ids.id','=',invoice_id.id)])
                    payment_info = invoice_id._get_payments_reconciled_info()
                    dict_payment_id = payment_info['content'][0]['payment_id']
                    move_id = payment_info['content'][0]['move_id']
                    move_id = self.env['account.move'].browse(move_id)
                    move_line = self.env['account.move.line'].browse(dict_payment_id)
                    move_line.with_context({'move_id': invoice_id.id}).remove_move_reconcile()
                    
                    vals = {'move_id': invoice_id.id,
                           'refund_method': 'refund',
                           'reason': 'Return Merchandise Exchange'}
                    amr = self.env['account.move.reversal'].with_context(active_ids=invoice_id.id, active_model='account.move').create(vals)
                    amr._compute_from_moves()
                    rev_invoice_id = amr.itl_reverse_moves()
                    rev_invoice_id.amount_total = 0
                    qty = sum(sale_id.order_line.mapped('product_uom_qty'))
                    for l in rev_invoice_id.invoice_line_ids:
                        l.quantity = qty
                    rev_invoice_id._move_autocomplete_invoice_lines_values()
                    rev_invoice_id.action_post()
                    to_reconcile = invoice_id._get_payments_widget_to_reconcile_info()
                    m_lines = invoice_id._get_reversal_move_line()
                    ml_to_add = m_lines.filtered(lambda i: i.move_id.id in [rev_invoice_id.id, move_id.id])
                    for ml in ml_to_add:
                        invoice_id.js_assign_outstanding_line(ml.id)
                        
                    if len(sale_id.invoice_ids) != 0:
                        rme_invoice_id = sale_id.invoice_ids[0]
                        rme_lines = invoice_id._get_reversal_move_line()
                        rme_lines_to_add = rme_lines.filtered(lambda i: i.move_id.id in [move_id.id])
                        for rme_ml in rme_lines_to_add:
                            rme_invoice_id.js_assign_outstanding_line(rme_ml.id)
        #raise ValidationError("Testing...")
        return rec
    
    def button_unreconcile(self):
        if self.picking_type_code in ['outgoing'] and self.sale_id.itl_is_rme:
            picking_type_id = self.env['stock.picking.type'].search([('warehouse_id','=',self.sale_id.itl_warehouse_return_id.id),('code','=','incoming')])
            
            defaults = {'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                       'picking_type_id': picking_type_id.id}
            vals = {
                'partner_id': self.partner_id.id,
                'picking_type_id': picking_type_id.id,
                'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                'immediate_transfer': True,
                'origin': self.origin,
                'sale_id': self.sale_id.id
            }
            lines = []
            origin_picking = self.sale_id.itl_sale_origin_id.picking_ids.filtered(lambda i: i.picking_type_code == 'outgoing')
            lot_id = False
            if origin_picking and origin_picking[0].move_line_ids_without_package:
                lot_id = origin_picking[0].move_line_ids_without_package[0].lot_id.id
            customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()
            for line in self.move_line_ids_without_package:
                val_line = {
                    'product_id': line.product_id.id,
                    'location_id': customerloc.id,
                    'location_dest_id': self.sale_id.itl_warehouse_return_id.lot_stock_id.id,
                    'qty_done': line.qty_done,
                    'product_uom_id': line.product_uom_id.id,
                    'lot_id': lot_id
                }
                lines.append((0, 0, val_line))
            
            vals.update(move_line_ids_without_package=lines)
            new_recepit = self.env['stock.picking'].create(vals)
            new_recepit.location_id = customerloc
            self.itl_exchange_receipt_id = new_recepit
            self.print_invoice(with_return=False)
        raise ValidationError("## Testing")

                    
    def button_reconcile(self):
        if self.picking_type_code in ['incoming'] and self.sale_id and self.sale_id.itl_sale_origin_id:
            if len(self.sale_id.itl_sale_origin_id.invoice_ids) != 0:
                invoice_id = self.sale_id.itl_sale_origin_id.invoice_ids[0]
                invoice_payment_state = invoice_id.invoice_payment_state
                if invoice_payment_state == 'paid':
                    payment_id = self.env['account.payment'].search([('invoice_ids.id','=',invoice_id.id)])
                    payment_info = invoice_id._get_payments_reconciled_info()
                    dict_payment_id = payment_info['content'][0]['payment_id']
                    move_id = payment_info['content'][0]['move_id']
                    move_line = self.env['account.move.line'].browse(dict_payment_id)
                    move_line.with_context({'move_id': invoice_id.id}).remove_move_reconcile()
        raise ValidationError("## Testing")
        
    
    def print_invoice(self, with_return=True):
        if self.picking_type_id.code == 'outgoing':
            if self.sale_id:
                if self.sale_id.invoice_count == 0:
                    sale_id = self.sale_id
                    partner_id = sale_id.partner_id.sudo()
                    temporal_vat = False
                    if sale_id.invoice_count == 0:
                        if partner_id.vat:
                            temporal_vat = partner_id.vat
                        if partner_id.itl_is_invoice_required:
                            if not partner_id.vat:
                                raise UserError("El contacto no tiene un RFC valido.")
                            if not partner_id.itl_payment_method_id:
                                raise UserError("El contacto no tiene forma de pago.")
                            if not partner_id.itl_usage:
                                raise UserError("El contacto no tiene uso de CFDI.")
                            if not partner_id.property_payment_term_id:
                                raise UserError("El contacto no tiene plazo de pago.")
                        else:
                            temporal_vat = partner_id.vat
                            partner_id.vat = False
                        itl_invoice = sale_id._create_invoices()
                        partner_id.vat = temporal_vat
                        itl_invoice.l10n_mx_edi_payment_method_id = partner_id.itl_payment_method_id.id
                        itl_invoice.l10n_mx_edi_usage = partner_id.itl_usage
                        itl_invoice.action_post()
                        msg = _("La factura fue creada y timbrada correctamente en la %s") % sale_id.name
                        self.message_post(body=msg)
                    if with_return:
                        return self.sale_id.invoice_ids[0].action_invoice_print()
                else:
                    if with_return:
                        return self.sale_id.invoice_ids[0].action_invoice_print()
            else:
                raise ValidationError("Este movimiento no tiene una orden de venta relacionada.")
    
    def send_shipping_email(self):
        #self.email_validations()
        shipping_template_id = self.env.ref('itl_inventory_moving.email_template_shipping_transfer_picking', False)
        
        if shipping_template_id:
            self.env['mail.template'].browse(shipping_template_id.id).send_mail(self.id, force_send=True)
            
    def send_shipping_email_sale(self):
        #self.email_validations()
        shipping_template_id = self.env.ref('itl_inventory_moving.email_template_shipping_sale_picking', False)
        
        if shipping_template_id:
            self.env['mail.template'].browse(shipping_template_id.id).send_mail(self.id, force_send=True)
            
    def send_receiving_email(self, base_url, new_picking):
        #self.email_validations()
        receiving_template_id = self.env.ref('itl_inventory_moving.email_template_receiving_transfer_picking', False)
        email_values = {'base_url': base_url,
                       'new_picking': new_picking.name}
        if receiving_template_id:
            self.env['mail.template'].browse(receiving_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)
            
    def send_receiving_return_email(self):
        #self.email_validations()
        receiving_template_id = self.env.ref('itl_inventory_moving.email_template_receiving_return_picking', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        email_values = {'base_url': base_url}
        if receiving_template_id:
            self.env['mail.template'].browse(receiving_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)
            
    def send_logistic_email(self):
        #self.email_validations()
        logistic_template_id = self.env.ref('itl_inventory_moving.email_template_shipping_logistic_company', False)
        
        if logistic_template_id:
            self.env['mail.template'].browse(logistic_template_id.id).send_mail(self.id, force_send=True)
    
    def send_employee_email(self):
        #self.email_validations()
        employee_template_id = self.env.ref('itl_inventory_moving.email_template_shipping_employee', False)
        
        if employee_template_id:
            self.env['mail.template'].browse(employee_template_id.id).send_mail(self.id, force_send=True)
    
    def email_validations(self):
        if not self.itl_is_rme and not self.sale_id:
            if not self.itl_pickup_date:
                raise ValidationError("Falta indicar Pickup date")
            if self.itl_delivery_by not in ['collected_employee'] and not self.itl_delivery_date:
                raise ValidationError("Falta indicar Delivery date")
        if self.itl_delivery_by == 'logistic_company':
            if not self.itl_logistic_company_email:
                raise ValidationError("Falta indicar Logistic company email")
        if self.itl_delivery_by == 'employee':
            if not self.itl_employee_email:
                raise ValidationError("Falta indicar Employee email")
        if self.picking_type_id.code == 'interal':
            if not self.itl_origin_email:
                raise ValidationError("Falta indicar Employee email")
    
    def create_purchase(self):
        purchase_obj = self.env['purchase.order']
        vals = {
            'partner_id': self.itl_logistic_company_id.id,
            'date_order': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'order_line': [(0, 0, {'product_id': self.env.company.itl_logistic_product_id.id, 
                                   'name': self.env.company.itl_logistic_product_id.display_name,
                                  'product_qty': 1,
                                  'price_unit': 0,
                                  'product_uom': self.env.company.itl_logistic_product_id.uom_po_id.id,
                                  'date_order': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   'taxes_id': [(6, 0, self.env.company.itl_logistic_product_id.supplier_taxes_id.ids)]
                                  })]
        }
        
        purchase_id = purchase_obj.sudo().create(vals)
        
        self.itl_purchase_id = purchase_id
        
    def get_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.date_done:
            return ""
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.date_done.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        return display_date_result
    
    def get_fecha_recoleccion_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.itl_pickup_date:
            return ""
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.itl_pickup_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        return display_date_result
    
    def get_fecha_entrega_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.itl_delivery_date:
            return ""
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.itl_delivery_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        return display_date_result
    
    def get_base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        
        return base_url
    
    def itl_action_return(self):
        vals = {'picking_id': self.id}
        #vals = {}
        #srp = self.env['stock.return.picking'].with_context(active_id=self.id).create(vals)
        srp = self.env['stock.return.picking'].with_context(active_id=self.id).create(vals)
        
        srp._onchange_picking_id()
        
        return srp.create_returns()
        
    def itl_prepare_picking(self):
        flag = self.env.user.has_group('itl_inventory_moving.group_itl_prepare_picking')
        if not flag:
            raise ValidationError("You are not allowed to prepare movements.")
        self.itl_check_availability()
        view = self.env.ref('itl_inventory_moving.itl_prepare_picking_form')
        view_id = view and view.id or False
        context = dict(self._context or {})
        pp_obj = self.env['itl.prepare.picking'].create({})
        context['pp_id'] = pp_obj.id
        return {
            'name': 'Prepare picking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.prepare.picking',
            'res_id': pp_obj.id,
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }
    
    def itl_prepare_picking_two(self):
        flag = self.env.user.has_group('itl_inventory_moving.group_itl_validate_picking')
        if not flag:
            raise ValidationError("You are not allowed to validate movements.")
        view = self.env.ref('itl_inventory_moving.itl_prepare_picking_2_form')
        view_id = view and view.id or False
        context = dict(self._context or {})
        pp_obj = self.env['itl.prepare.picking.two'].create({})
        context['pp_id'] = pp_obj.id
        return {
            'name': 'Prepare picking',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'itl.prepare.picking.two',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
            'flags': {'form': {'action_buttons': False}}
        }
        
    def action_cancel(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'is_locked': True, 'state': 'cancel'})
        return True
    
    @api.onchange('location_dest_id')
    def _onchange_location_dest_id(self):
        if self.location_dest_id:
            for line in self.move_line_ids_without_package:
                line.location_dest_id = self.location_dest_id
    
    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            for line in self.move_line_ids_without_package:
                line.location_id = self.location_id
                line.lot_id = False
    
    def action_back_to_draft(self):
        moves = self.mapped("move_lines")
        moves.action_back_to_draft()
        stock_move_line_ids = self.mapped("move_line_ids")
        for sml in stock_move_line_ids:
            sml.state = 'draft'
        self.write({"state": "draft"})
    
    # Inherit
    def action_confirm(self):
        super(Picking, self).action_confirm()
        self._onchange_location_id()
        
    # Function to check availability, if not, a new line is added
    def itl_check_availability(self):
        for picking in self:
            # First, execute default method to check availability
            picking.action_assign()
            # After that, if there are no availability, try to add a new line
            if len(picking.move_line_ids_without_package) == 0:
                move_obj = self.env['stock.move.line']
                for move in picking.mapped('move_lines'):
                    qty = move.product_uom_qty
                    vals = move._prepare_move_line_vals(qty)
                    
                    move_line = {'picking_id': picking.id,
                            'product_id': move.product_id.id,
                            'move_id': move.id,
                            'location_id': picking.location_dest_id.id,
                            'location_dest_id': vals['location_dest_id'],
                            'qty_done': qty,
                            'product_uom_id':vals['product_uom_id'],
                            'lot_id': False,
                            'lot_name': False
                    }
                    
                    move_obj.create(move_line)
    
class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"
    
    def _create_returns(self):
        res = super(StockReturnPicking, self)._create_returns()
        move_obj = self.env['stock.move.line']
        assigned_moves = self.env['stock.move']
        origin_picking_id = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        pick_id = self.env['stock.picking'].browse(res[0])
        pick_id.itl_is_return = True
        pick_id.itl_delivery_by = False
        pick_id.itl_transfer_origin = False
        pick_id.itl_driver_name = False
        pick_id.itl_type_of_car = False
        pick_id.itl_plate_of_car = False
        pick_id.itl_delivery_by = False
        pick_id.itl_pickup_date = False
        pick_id.itl_delivery_date = False
        pick_id.itl_logistic_company_id = False
        pick_id.itl_logistic_company_email = False
        pick_id.itl_employee_partner_id = False
        pick_id.itl_purchase_id = False
        pick_id.immediate_transfer = True
        pick_id.itl_origin_sale = self.picking_id.origin
        pick_id._get_address()
        pick_id._get_warehouse()
        for move in pick_id.mapped('move_lines').filtered(lambda x:x.state == 'assigned' and x.origin_returned_move_id and x.product_id.tracking == 'lot'):
            if len(move.origin_returned_move_id.move_line_ids) ==1:
                move.move_line_ids.unlink()
                qty = move.product_uom_qty
                line = move.origin_returned_move_id.move_line_ids
                qty_todo = min(qty , line.qty_done)
                vals = move._prepare_move_line_vals(qty_todo)
                val = {'picking_id': vals['picking_id'],
                                    'product_id': vals['product_id'],
                                    'move_id':move.id,
                                    'location_id':origin_picking_id.location_dest_id.id,
                                    'location_dest_id':vals['location_dest_id'],
                                    'qty_done':qty_todo,
                                    'product_uom_id':vals['product_uom_id'],
                                    'lot_id':line.lot_id and line.lot_id.id or False,
                                    'lot_name':line.lot_id and line.lot_id.name or False}
                move_obj.create(val)
            assigned_moves |= move
        if assigned_moves:
            assigned_moves.write({'state': 'draft'})
        return res
