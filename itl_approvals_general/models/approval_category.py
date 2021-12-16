
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'
    
    
    code = fields.Char(string="Code")
    approval_hierarchy = fields.Boolean(string="Jerarquía de aprobación", default=True, help="Si está activada cada usuario aprobará en el orden de la tabla.")
    has_product = fields.Selection(
        CATEGORY_SELECTION, string="Has Product", default="no", required=True,
        help="Additional products that should be specified on the request.")
    approval_by = fields.Selection([('only_user','Solo por usuarios'),
                                    ('user_and_department','Departamentos y usuarios'),
                                   ('user_and_so_type','Tipo de SO y usuarios (solo para SO)')], string="Forma de aprobación", 
                                  help="Indica si la aprobación será solo para usuarios o para departamentos y usuarios.", default='only_user')
    approval_department_user_ids = fields.One2many('approval.department.user', 'approval_category_id', string="Departamentos y usuarios", copy=True)
    approval_so_type_user_ids = fields.One2many('approval.so.type.user', 'approval_category_id', string="Tipo de SO y usuarios (solo para SO)", copy=True)
    product_id = fields.Many2one('product.product', string="Producto")
    product_uom_id = fields.Many2one('uom.uom', string="Unidad de medida")
    min_boxes = fields.Integer(string="Casos <=")
    max_boxes = fields.Integer(string="Casos >=")
    
class ApprovalDepartmentUser(models.Model):
    _name = 'approval.department.user'
    
    
    approval_category_id = fields.Many2one('approval.category')
    approval_hierarchy = fields.Boolean(string="Jerarquía de aprobación", default=True, help="Si está activada cada usuario aprobará en el orden de la tabla.")
    department_id = fields.Many2one('hr.department', string="Departamento")
    #user_ids = fields.Many2many('res.users', string="Approvers")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    
    approval_sequence_user_ids = fields.One2many('approval.sequence.user', 'approval_department_user_id', string="Approvers", copy=True)
    
    @api.constrains('approval_sequence_user_ids')
    def _onchange_sequence(self):
        #_logger.info("---> _onchange_sequence context: " + str(self._context))
        if self.approval_sequence_user_ids:
            sequences = self.approval_sequence_user_ids.mapped('sequence')
            users = [item.user_id.id for item in self.approval_sequence_user_ids]
            #_logger.info("--> users: " + str(users))
            #if any(sequences.count(x) > 1 for x in sequences):
            #    raise UserError("El número de secuencia debe ser único.")
            #if any(users.count(x) > 1 for x in users):
            #    raise UserError("El usuario aprobador debe ser único por departamento.")
            #if any(x == 0 for x in sequences):
            #    raise UserError("El número de secuencia debe ser mayor a 0.")
                

class ApprovalSOtypeUser(models.Model):
    _name = 'approval.so.type.user'
    
    
    approval_category_id = fields.Many2one('approval.category')
    approval_hierarchy = fields.Boolean(string="Jerarquía de aprobación", default=True, help="Si está activada cada usuario aprobará en el orden de la tabla.")
    so_type_id = fields.Many2one('sale.order.type', string="SO type")
    proposer_user_ids = fields.Many2many('res.users', 'user_proposer', 'user_id', 'proposer_id', string="Proposers")
    boxes_conditions = fields.Selection([('less_than','Menor igual'),('greater_than','Mayor igual')], string="Casos")
    #boxes_qty = fields.Integer(string="Cajas")
    #user_ids = fields.Many2many('res.users', 'user_approver', 'user_id', 'approver_id', string="Approvers")
    approval_minimum = fields.Integer(string="Minimum Approval", default="1", required=True)
    
    approval_sequence_user_ids = fields.One2many('approval.sequence.user.so.type', 'approval_so_type_user_id', string="Approvers", copy=True)
    
    @api.constrains('approval_sequence_user_ids')
    def _onchange_sequence(self):
        _logger.info("--> _onchange_sequence")
        if self.approval_sequence_user_ids:
            sequences = self.approval_sequence_user_ids.mapped('sequence')
            users = [item.user_id.id for item in self.approval_sequence_user_ids]
    
class ApprovalSequenceUser(models.Model):
    _name = 'approval.sequence.user'
    _rec_name = 'user_id'
    
    approval_department_user_id = fields.Many2one('approval.department.user')
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=1, required=True)
    user_id = fields.Many2one('res.users', string="Approver", required=True)
    
class ApprovalSequenceSOtypeUser(models.Model):
    _name = 'approval.sequence.user.so.type'
    _rec_name = 'user_id'
    
    
    approval_so_type_user_id = fields.Many2one('approval.so.type.user')
    sequence = fields.Integer('sequence', help="Sequence for the handle.", default=1, required=True)
    user_id = fields.Many2one('res.users', string="Approver", required=True)