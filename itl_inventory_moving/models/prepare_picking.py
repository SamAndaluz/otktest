
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from pytz import timezone
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class PreparePicking(models.TransientModel):
    _name = "itl.prepare.picking"
    _description = "Prepare picking"
    _rec_name = "id"
    
    
    itl_pickup_date = fields.Datetime('Pickup Date')
    itl_delivery_date = fields.Datetime('Delivery Date')
    itl_delivery_by = fields.Selection([('logistic_company','Logistic company'),('employee','Employee')], string="Delivery by")
    itl_employee_partner_id = fields.Many2one('res.partner', string="Employee contact")
    itl_employee_email = fields.Char(related="itl_employee_partner_id.email", string="Employee email")
    itl_logistic_company_id = fields.Many2one('res.partner', string="Logistic company")
    itl_logistic_company_email = fields.Char(related="itl_logistic_company_id.email", string="Logistic company email")
    itl_driver_name = fields.Char(string="Driver's name")
    itl_type_of_car = fields.Char(string="Type of car")
    itl_plate_of_car = fields.Char(string="Plate of car")
    
    itl_stock_move_line_id = fields.Many2many('stock.move.line')
    itl_stock_picking_ids = fields.Many2many('stock.picking')
    
    def get_fecha_recoleccion_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.itl_pickup_date:
            return "No especificada"
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.itl_pickup_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        return display_date_result
    
    def get_fecha_entrega_datetime(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        if not self.itl_delivery_date:
            return "No especificada"
        display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(self.itl_delivery_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d/%m/%Y %H:%M:%S")
        return display_date_result
    
    
    @api.model
    def default_get(self, fields):
        res = super(PreparePicking, self).default_get(fields)
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        res['itl_stock_picking_ids'] = [(6, 0, picking_ids.ids)]
        invalid_pickings = picking_ids.filtered(lambda i: i.state in ['done','cancel'])
        if len(invalid_pickings) > 0:
            raise ValidationError("You can't prepare Done movements, Cancelled movements.")
        wrong_pickings = picking_ids.filtered(lambda i: i.picking_type_id.code == 'incoming' or i.itl_sequence_code == 'PICK' or i.itl_transfer_origin)
        if len(wrong_pickings) > 0:
            raise ValidationError("You can only prepare Delivery Orders and Outgoing Transfers.")
        origin_warehouse = picking_ids.mapped('itl_location_warehouse_id')
        if len(origin_warehouse) != 1:
            raise ValidationError("You can't prepare delivery orders from different warehouse at same.")
        stock_move_line_ids = self.env['stock.move.line'].search([('picking_id','in',self.env.context.get('active_ids'))])
        
        _logger.info("---> picking_ids: " + str(picking_ids.ids))
        _logger.info("---> move line picking_ids: " + str(stock_move_line_ids.mapped('picking_id').ids))
        
        missing_pickings = []
        for orig_pick_id in picking_ids.ids:
            if orig_pick_id not in stock_move_line_ids.mapped('picking_id').ids:
                missing_pickings.append(orig_pick_id)
                
        if len(missing_pickings) > 0:
            picking_ids = self.env['stock.picking'].browse(missing_pickings)
            picking_names = picking_ids.mapped('name')
            raise ValidationError("The next movements haven't product lines: " + str(picking_names))
        
        res['itl_stock_move_line_id'] = [(6, 0, stock_move_line_ids.ids)]
        
        return res
    
    def process_picking(self):
        qty_done_ok = False if 0 in self.itl_stock_move_line_id.mapped('qty_done') or len(self.itl_stock_move_line_id) == 0 else True
        if not qty_done_ok:
            raise ValidationError("Some movements have quantity Done as 0, please check it.")
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        for picking in picking_ids:
            picking.itl_pickup_date = self.itl_pickup_date
            picking.itl_delivery_date = self.itl_delivery_date
            picking.itl_delivery_by = self.itl_delivery_by
            picking.itl_employee_partner_id = self.itl_employee_partner_id
            picking.itl_logistic_company_id = self.itl_logistic_company_id
            picking.itl_driver_name = self.itl_driver_name
            picking.itl_type_of_car = self.itl_type_of_car
            picking.itl_plate_of_car = self.itl_plate_of_car
            picking.itl_first_review = True
            
            display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(fields.Datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(timezone('America/Mexico_City')),"%Y-%m-%d %H:%M:%S")
            picking.itl_first_date_review = display_date_result
            picking.state = 'assigned'
            
        self.send_email_to_source_warehouse()
        
        if self.itl_delivery_by == 'logistic_company':
            self.send_logistic_email()
        if self.itl_delivery_by == 'employee':
            self.send_employee_email()
            
        
    
    def send_email_to_source_warehouse(self):
        #self.email_validations()
        shipping_template_id = self.env.ref('itl_inventory_moving.email_template_multiple_shipping_sale_picking', False)
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        partner_to = picking_ids[0].itl_origin_contact_id
        if not partner_to or not partner_to.email:
            return
        origin_warehouse = picking_ids[0].itl_location_warehouse_id
        email_values = {'partner_to_id': partner_to.id,
                       'partner_to_name': partner_to.name,
                       'warehouse_name': origin_warehouse.name}
        if shipping_template_id:
            self.env['mail.template'].browse(shipping_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)
            
    def send_logistic_email(self):
        #self.email_validations()
        logistic_template_id = self.env.ref('itl_inventory_moving.email_template_multiple_shipping_logistic', False)
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        partner_to = self.itl_logistic_company_id
        if not partner_to or not partner_to.email:
            return
        email_values = {'partner_to_id': partner_to.id,
                       'partner_to_name': partner_to.name}
        if logistic_template_id:
            self.env['mail.template'].browse(logistic_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)
            
    def send_employee_email(self):
        #self.email_validations()
        employee_template_id = self.env.ref('itl_inventory_moving.email_template_multiple_shipping_employee', False)
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        partner_to = self.itl_employee_partner_id
        if not partner_to or not partner_to.email:
            return
        email_values = {'partner_to_id': partner_to.id,
                       'partner_to_name': partner_to.name}
        if employee_template_id:
            self.env['mail.template'].browse(employee_template_id.id).with_context(email_values).send_mail(self.id, force_send=True)
            
    def email_validations(self):
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
                
    def get_base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/itl_inventory_moving/show_moves?active_ids=%d' % ('stock.picking')
        
        return base_url
    
class PreparePickingTwo(models.TransientModel):
    _name = "itl.prepare.picking.two"
    _description = "Prepare picking two"
    
    
    itl_pickup_date = fields.Datetime('Pickup Date')
    itl_delivery_date = fields.Datetime('Delivery Date')
    itl_delivery_by = fields.Selection([('logistic_company','Logistic company'),('employee','Employee')], string="Delivery by")
    itl_employee_partner_id = fields.Many2one('res.partner', string="Employee contact")
    itl_employee_email = fields.Char(related="itl_employee_partner_id.email", string="Employee email")
    itl_logistic_company_id = fields.Many2one('res.partner', string="Logistic company")
    itl_logistic_company_email = fields.Char(related="itl_logistic_company_id.email", string="Logistic company email")
    itl_driver_name = fields.Char(string="Driver's name")
    itl_type_of_car = fields.Char(string="Type of car")
    itl_plate_of_car = fields.Char(string="Plate of car")
    
    itl_stock_move_line_id = fields.Many2many('stock.move.line')
    
    
    @api.model
    def default_get(self, fields):
        res = super(PreparePickingTwo, self).default_get(fields)
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        #res['itl_pickup_date'] = picking_ids[0].itl_pickup_date
        #res['itl_delivery_date'] = picking_ids[0].itl_delivery_date
        #res['itl_delivery_by'] = picking_ids[0].itl_delivery_by
        #res['itl_employee_partner_id'] = picking_ids[0].itl_employee_partner_id.id
        #res['itl_employee_email'] = picking_ids[0].itl_employee_email
        #res['itl_logistic_company_id'] = picking_ids[0].itl_logistic_company_id.id
        #res['itl_logistic_company_email'] = picking_ids[0].itl_logistic_company_email
        #res['itl_driver_name'] = picking_ids[0].itl_driver_name
        #res['itl_type_of_car'] = picking_ids[0].itl_type_of_car
        #res['itl_plate_of_car'] = picking_ids[0].itl_plate_of_car
        
        invalid_pickings = picking_ids.filtered(lambda i: i.state in ['done','cancel'] or not i.itl_first_review)
        if len(invalid_pickings) > 0:
            raise ValidationError("You can't prepare Done movements, Cancelled movements or not prepared movements.")
        wrong_pickings = picking_ids.filtered(lambda i: i.picking_type_id.code == 'incoming' or i.itl_sequence_code == 'PICK' or i.itl_transfer_origin)
        if len(wrong_pickings) > 0:
            raise ValidationError("You can only prepare Delivery Orders and Outgoing Transfers.")
        origin_warehouse = picking_ids.mapped('itl_location_warehouse_id')
        if len(origin_warehouse) != 1:
            raise ValidationError("You can't prepare delivery orders from different warehouse at same.")
        stock_move_line_ids = self.env['stock.move.line'].search([('picking_id','in',self.env.context.get('active_ids'))])
        res['itl_stock_move_line_id'] = [(6, 0, stock_move_line_ids.ids)]
        
        return res
    
    def validate_picking(self):
        picking_ids = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        for picking in picking_ids:
            picking.button_validate()
            
        return {'type': 'ir.actions.act_window_close'}