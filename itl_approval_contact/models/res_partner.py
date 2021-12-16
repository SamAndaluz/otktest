from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class partner_extended(models.Model):
    _inherit = 'res.partner'
    
    
    state = fields.Selection([('new','Nuevo'),('to_approve','Para aprobar'),('approved','Aprobado'),('rejected','Rechazado'),('cancel', 'Cancelled')], string="Status", copy=False, default="new")
    approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status")
    
    
    def send_to_approve(self):
        if not self.env.company.itl_so_approval_category_id:
            raise ValidationError("Approval category is not configured.")

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Contacto - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_partner_approval_category_id.id,
            'partner_id': self.id,
        }

        
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
        
        self.sudo().approval_request_id = rec.id
        
        self.sudo().state = 'to_approve'
        
        self.message_post_with_view('itl_approval_contact.message_approval_contact_created_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)
        
        rec.message_post_with_view('mail.message_origin_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)
    
    def reset_to_new(self):
        self.sudo().state = 'new'
        
    def write(self, vals):
        self = self.sudo()
        return super(partner_extended, self).write(vals)