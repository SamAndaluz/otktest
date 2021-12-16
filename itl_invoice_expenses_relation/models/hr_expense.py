# -*- coding: utf-8 -*-

from odoo import models, fields, api


class itl_invoice_expenses_relation(models.Model):
    _inherit = "hr.expense"
    
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    partner_id = fields.Many2one('res.partner', string='Vendor', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
    invoice_related_id = fields.Many2one('account.move', string="Related Bill", readonly=False)
    invoice_date = fields.Date(related="invoice_related_id.invoice_date", string="Bill date", readonly=True)
    invoice_amount_total = fields.Monetary(related="invoice_related_id.amount_total", string="Bill amount total", readonly=True)
    invoice_amount_untaxed = fields.Monetary(related="invoice_related_id.amount_untaxed", string="Bill amount untaxed", readonly=True)
    
    def search_bill(self):
        if self.reference:
            invoice_id = self.env['account.move'].search([('ref','ilike',self.reference),('partner_id','=',self.partner_id.id),('type','=','in_invoice'),('state','=','posted')])
            if invoice_id:
                self.invoice_related_id = invoice_id[0]
            else:
                self.invoice_related_id = False
    
    def attach_bill(self):
        if self.invoice_related_id:
            Model = self.env['ir.attachment']
            
            invoice_file_attached = Model.search([('res_model','=','account.move'),('res_id','=',self.invoice_related_id.id),('mimetype','=','application/xml')])
            
            if invoice_file_attached:
                filename = invoice_file_attached.name
                
                expense_invoice_attached = Model.search([('res_model','=','hr.expense'),('res_id','=',self.id),('mimetype','=','application/xml'),('name','=',filename)])
                
                if not expense_invoice_attached:
                    try:
                        attachment = Model.create({
                            'name': filename,
                            'datas': invoice_file_attached.datas,
                            'res_model': 'hr.expense',
                            'res_id': int(self.id)
                        })
                        attachment._post_add_create()
                    except Exception:
                        _logger.exception("Fail to upload attachment %s" % filename)
            else:
                self.message_post(body="Related bill has not xml file.")