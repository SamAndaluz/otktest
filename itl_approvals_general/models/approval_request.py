from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
from datetime import date

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequestCustom(models.Model):
    _inherit = 'approval.request'
    
    
    company_id = fields.Many2one('res.company', string='Company',  default=lambda self: self.env.company)
    category_code = fields.Char(related='category_id.code')
    next_approver_id = fields.Many2one('res.users', string="Next approver", readonly=True, store=True)
    approval_hierarchy = fields.Boolean(related="category_id.approval_hierarchy")
    
    has_product = fields.Selection(related="category_id.has_product")
    product_line_ids = fields.One2many('approval.product.line', 'approval_request_id', check_company=True)
    
    request_origin = fields.Char(string="Origin", compute="_get_origin")
    partner_origin = fields.Char(string="Contact", compute="_get_origin")
    amount_origin = fields.Float(string="Amount", compute="_get_origin")
    
    #number = fields.Char(string='Number', required=True, copy=False, readonly=True, states={'new': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    
    def _get_origin(self):
        for rq in self:
            rq.request_origin = ""
            rq.partner_origin = ""
            rq.amount_origin = 0.0
            if rq.purchase_id:
                rq.request_origin = rq.purchase_id.name
                rq.amount_origin = rq.purchase_id.amount_total
                rq.partner_origin = rq.purchase_id.partner_id.name
                return
            if rq.sale_id:
                rq.request_origin = rq.sale_id.name
                rq.amount_origin = rq.sale_id.amount_total
                rq.partner_origin = rq.sale_id.partner_id.name
                return
            if rq.partner_id:
                rq.partner_origin = rq.partner_id.name
                return

    # Inherit fields
    request_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], default="new", compute="_compute_request_status", store=True, compute_sudo=True, group_expand='_read_group_request_status')
    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], compute="_compute_user_status")
    
    #Inherit method
    def action_approve(self, approver=None):
        rec = super(ApprovalRequestCustom, self).action_approve()
        # Siempre será por jerarquía
        #if self.category_id.approval_hierarchy:
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        approver_names = approvers.mapped("user_id.name")
        _logger.info("---> generals action_approve")
        if len(approvers) > 0:
            self.write({'next_approver_id': approvers[0].user_id.id})
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
            self.send_approval_email_notification()
        else:
            self.send_email_notification_done()
        
    def action_refuse_confirm(self, approver=None):
        _logger.info("----####> action_refuse_confirm")
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                    lambda approver: approver.user_id == self.env.user
                )
        approver.write({'status': 'refused'})
        self.send_email_notification_done()
        self.sudo()._get_user_approval_activities(user=self.env.user).action_feedback()
    
    #Inherit method
    def action_confirm(self):
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
            
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        #approver_names = approvers.mapped("user_id.name")
        _logger.info("---> action_confirm")
        
        approval_hierarchy = False
        
        if self.category_id.approval_by == 'only_user':
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
            #approver_names = approvers.mapped("user_id.name")

            #if not self.category_id.approval_hierarchy and len(self.approver_ids) < self.approval_minimum:
            #    raise UserError(_("You have to add at least %s approvers to confirm your request.") % self.approval_minimum)
            
            #if self.category_id.approval_hierarchy:
            approval_hierarchy = True
        
        if self.category_id.approval_by == 'user_and_department':
            #approval_department_id = self.get_approval_department()
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
            _logger.info("--> approvers: " + str(approvers))
            #approver_names = approvers.mapped("user_id.name")
            
            #if approval_department_id.approval_hierarchy and len(self.approver_ids) < approval_department_id.approval_minimum:
            #    raise UserError(_("You have to add at least %s approvers to confirm your request.") % approval_department_id.approval_minimum)
            
            #if approval_department_id.approval_hierarchy:
            #_logger.info("#### DEPARTAMENTO ES JERARQUÍA ####")
            approval_hierarchy = True
            
        if self.category_id.approval_by == 'user_and_so_type':
            #_logger.info("---> user_and_so_type")
            #approval_so_type_id = self.get_approval_so_type()
            #_logger.info("---> approval_so_type_id: " + str(approval_so_type_id))
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
            
        # Siempre será por jerarquía
        #if approval_department_id.approval_hierarchy:
        _logger.info("--> approvers: " + str(approvers))
        if len(approvers) != 0:
            self.write({'next_approver_id': approvers[0].user_id.id})
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        else:
            self.action_approve()
            self.request_status = 'approved'
        #else:
        #    approvers._create_activity()
        #    approvers.write({'status': 'pending'}) 

        self.write({'date_confirmed': fields.Datetime.now()})
        #raise UserError("***--Testing")
        
    def send_approval_email_notification(self):
        template_id = self.env.ref('itl_approvals_general.itl_approval_email_notification', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        email_values = {'base_url': base_url}
        if template_id:
            self.env['mail.template'].browse(template_id.id).with_context(email_values).with_user(1).send_mail(self.id, force_send=True)
            
    def send_email_notification_done(self):
        template_id = self.env.ref('itl_approvals_general.itl_approval_email_notification_done', False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        approval_status = dict(self._fields['request_status'].selection).get(self.request_status)
        email_values = {'base_url': base_url,
                       'approval_status': approval_status}
        if template_id:
            self.env['mail.template'].browse(template_id.id).with_context(email_values).with_user(1).send_mail(self.id, force_send=True)
    
    def get_approval_so_type(self):
        _logger.info("---> get_approval_so_type: " )
        if self.sale_id:
            so_type_id = self.sale_id.type_id
            if not so_type_id:
                raise UserError("La SO no tiene un tipo de SO.")
            if len(self.category_id.approval_so_type_user_ids) == 0:
                raise UserError(("El campo 'Tipo de SO y usuarios' en la configuración de la categoría está vacío."))
            approval_flow_ids = self.category_id.approval_so_type_user_ids.filtered(lambda i: i.so_type_id == so_type_id and self.env.user.id in i.proposer_user_ids.ids)
            _logger.info("---> approval_flow_ids: " + str(approval_flow_ids))
            if len(approval_flow_ids) == 0:
                raise UserError(("No se encontró la combinación entre tipo de SO y el usuario actual en la configuración de la categoría de aprobación."))
            if len(approval_flow_ids) > 2:
                raise UserError(("Solo se permiten 2 configuraciones por usuario. Se encontraron " + str(len(approval_flow_ids)) + " para el usuario " + str(self.env.user.name)))
            if approval_flow_ids:
                approval_flow_id = False
                if len(approval_flow_ids) == 1:
                    so_type_id = approval_flow_ids[0]
                if len(approval_flow_ids) == 2:
                    boxes_conditions = approval_flow_ids.mapped('boxes_conditions')
                    if not all(boxes_conditions):
                        raise UserError(("El atributo Casos no está configurado en los flujos de aprobación del tipo de orden."))
                    so_product_ids = self.sale_id.order_line.filtered(lambda l: l.product_id.id == self.category_id.product_id.id and l.product_uom.id == self.category_id.product_uom_id.id)
                    if so_product_ids:
                        product_qty_list = so_product_ids.mapped('product_uom_qty')
                        product_qty_total = sum(product_qty_list)
                        if product_qty_total <= self.category_id.min_boxes:
                            so_type_id = approval_flow_ids.filtered(lambda a: a.boxes_conditions == 'less_than')
                        if product_qty_total >= self.category_id.max_boxes:
                            so_type_id = approval_flow_ids.filtered(lambda a: a.boxes_conditions == 'greater_than')
                    else:
                        raise UserError(("La SO relacionada no contiene el producto " + str(self.category_id.product_id.name) + " configurado en la categoría de aprobación o la unidad de medida de la línea de la SO no coincide con la unidad de medida " + str(self.category_id.product_uom_id.name) + " configurada en la categoría de aprobación."))

            if not so_type_id:
                raise UserError(("No se encontró el tipo de SO en la configuración de la categoría."))
            _logger.info("---> so_type_id: " + str(so_type_id.boxes_conditions))
            return so_type_id
        else:
            return UserError("El approval request no tiene una SO asociada.")
    
    def get_approval_department(self):
        if len(self.category_id.approval_department_user_ids) == 0:
            raise UserError(("El campo 'Departamentos y usuarios' en la configuración de la categoría está vacío."))
            
        user_department_id = self.check_user_department()
        department_id = self.category_id.approval_department_user_ids.filtered(lambda i: i.department_id == user_department_id)
            
        if len(department_id) != 1:
            raise UserError(("El departamento %s debe ser único en el campo 'Departamentos y usuarios' en la configuración de la categoría.") % user_department_id.name)
            
        return department_id
    
    def action_confirm_plus(self):
        if not self.category_id.approval_hierarchy and len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.") % self.approval_minimum)
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))

        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        approver_names = approvers.mapped("user_id.name")

        if self.category_id.approval_hierarchy:
            self.write({'next_approver_id': approvers[0].user_id.id})
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})

        else:
            approvers._create_activity()
            approvers.write({'status': 'pending'}) 

        self.write({'date_confirmed': fields.Datetime.now()})
    
    def check_user_department(self):
        current_user_id = self.env.user
        employee_id = current_user_id.employee_id
        if not employee_id:
            raise UserError(("El usuario %s no tiene un empleado relacionado.") % current_user_id.name)
        if not employee_id.department_id:
            raise UserError(("El usuario %s no tiene un departamento relacionado.") % current_user_id.name)
        
        return employee_id.department_id
        
    @api.onchange('category_id', 'request_owner_id')
    def _onchange_category_id(self):
        new_users = []
        new_user_dict = []
        current_user_id = self.env.user
        if self.category_id.approval_by == 'only_user':
            new_users = self.category_id.user_ids
            for n_unser in new_users:
                new_user_dict.append({'id': n_unser.id, 'sequence': n_unser.sequence})
        if self.category_id.approval_by == 'user_and_department':
            if len(self.category_id.approval_department_user_ids) == 0:
                raise UserError(("El campo 'Departamentos y usuarios' en la configuración de la categoría está vacío."))
            user_department_id = self.check_user_department()
            department_id = self.category_id.approval_department_user_ids.filtered(lambda i: i.department_id == user_department_id)
            if not department_id:
                raise UserError(("El departamento %s no se encontró en el campo 'Departamentos y usuarios' de la configuración de la categoría de aprobación %s.") % (user_department_id.name, self.category_id.name))
            if len(department_id) != 1:
                raise UserError(("El departamento %s debe ser único en el campo 'Departamentos y usuarios' en la configuración de la categoría.") % user_department_id.name)

            #new_users = department_id.user_ids
            new_users = department_id.approval_sequence_user_ids
            for n_unser in new_users:
                new_user_dict.append({'id': n_unser.user_id.id, 'sequence': n_unser.sequence})
                
        if self.category_id.approval_by == 'user_and_so_type':
            so_type_id = self.get_approval_so_type()
            new_users = so_type_id.approval_sequence_user_ids
            for n_unser in new_users:
                new_user_dict.append({'id': n_unser.user_id.id, 'sequence': n_unser.sequence})
            
        current_users = self.approver_ids.mapped('user_id')
        employee_user_id = False
        if self.category_id.is_manager_approver:
            employee = self.env['hr.employee'].search([('user_id', '=', self.request_owner_id.id)], limit=1)
            if employee.parent_id.user_id:
                employee_user_id = employee.parent_id.user_id
                #new_users |= employee_user_id
                if not any(x['id'] == employee_user_id.id for x in new_user_dict):
                    new_user_dict.append({'id': employee_user_id.id, 'sequence': 0})
        #final_users = new_users - current_users
        #final_users = final_users.filtered(lambda i: i.id != current_user_id.id)
        #final_users = new_user_dict.filtered(lambda i: i['id'] != current_user_id.id)
        final_users = [item for item in new_user_dict if item['id'] != current_user_id.id]
        #final_users_list = []
        #for user in final_users:
        #    final_users_list.append({'id': user.id, 'sequence': user.sequence})
        # Si tiene manager se coloca como el approver #1
        #if employee_user_id:
        #    for item in final_users_list:
        #        if item['id'] == employee_user_id.id:
        #            item['sequence'] = 0
        #            break
                
            #employee_user = next(item for item in final_users_list if item['id'] == employee_user_id.id)
            #employee_user['sequence'] = 0
        
        final_users_list = sorted(final_users, key = lambda i: i['sequence'])
        
        final_users_list_updated = []
        today = fields.Date.today()
        
        users_time_off = self.env['hr.leave'].sudo().search([('request_date_from','<=',today),('request_date_to','>=',today),('state','=','validate')])
        
        user_ids = users_time_off.mapped('user_id').ids
        
        for user in final_users_list:
            if user['id'] not in user_ids:
                final_users_list_updated.append(user)
        
        if len(final_users_list_updated) == 0:
            raise UserError("No hay usuarios aprobadores para este documento. Por favor contacte a su administrador.")
        
        for user in final_users_list_updated:
            self.approver_ids += self.env['approval.approver'].new({
                'user_id': user['id'],
                'request_id': self.id,
                'status': 'new'})
    
    def _get_all_approval_activities(self):
        domain = [
            ('res_model', '=', 'approval.request'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', self.env.ref('approvals.mail_activity_data_approval').id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities
    
    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            #minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('pending'):
                    status = 'pending'
                else:
                    status = 'new'
                if request.category_id.approval_by in ['only_user','user_and_department','user_and_so_type']:
                    if status_lst.count('approved') >= len(request.approver_ids):
                        status = 'approved'
                #if request.category_id.approval_by == 'user_and_department':
                #    if status_lst.count('approved') >= len(request.approver_ids):
                #        status = 'approved'
                #if request.category_id.approval_by == 'user_and_so_type':
                #    if status_lst.count('approved') >= len(request.approver_ids):
                #        status = 'approved'
            else:
                status = 'new'
            request.request_status = status

    def approve_requests(self):
        for request in self:
            request.action_approve()
            
    #@api.model
    #def create(self, vals):
    #    if vals.get("number", "/") == "/" and vals.get("category_id"):
    #        category_id = self.env["approval.category"].browse(vals["category_id"])
    #        if category_id.sequence_id:
    #            vals["number"] = category_id.sequence_id.next_by_id()
    #    return super(ApprovalRequestCustom, self).create(vals)
    
class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Rejected'),
        ('cancel', 'Cancel')], string="Status", default="new", readonly=True)