# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class itl_user_managers(models.Model):
    _inherit = 'res.users'
    itl_employee_subordinados = fields.Many2many("res.users",compute = "_compute_test")
    
    def _compute_test(self):
        current_user = self.env.user
        _logger.info("current_user: "  + str(current_user) )
        empleado = self.env['hr.employee'].search([('user_id', '=', int(current_user))])
        _logger.info("empleado: " + str(empleado))
        subordinados = empleado._get_subordinates()
        con = 0
        for record in subordinados:
            _logger.info("Dentro del for: "+str(con) + " - " + str(record))
            con = con + 1
            _logger.info("Record en for: " + str(record))
            _logger.info("Record to user: " + str(record.user_id))
            record = record.user_id
            _logger.info("record cambiado. " + str(record))
#             record.value2 = float(record.value) / 100
        _logger.info("Subordinados: " + str(subordinados))
        subordinados = subordinados.user_id
        _logger.info("Subordinados cambiado a user_id: " + str(subordinados))
        self.itl_employee_subordinados = subordinados
        
        
        
        
        
        #intento obtener
        #arreglo = {"41","19"}
        #_logger.info("--> ARREGLO; " + str(arreglo))
        #_logger.info("int(self.env.user): " + str(int(self.env.user)))
        #getSub = self.env['purchase.order'].search([('create_uid', 'in', arreglo)])
        #_logger.info("--> getSub: " + str(getSub))
        
        
        #obtener ordenes de subordinados
   
    

#class itl_users(models.Model):
#    _inherit = 'purchase.order'
#    campoFo = fields.Many2many("res.users",compute = "_compute_test")
    
#    def _compute_test(self):
#        current_user = self.env.user
#        _logger.info("current_user: "  + str(current_user) )
#        empleado = self.env['hr.employee'].search([('user_id', '=', int(current_user))])
#        _logger.info("empleado: " + str(empleado))
#        subordinados = empleado._get_subordinates()
#        _logger.info("Subordinados: " + str(subordinados))
   
    
                
                
                
                
                
        #empleado = self.env['hr.employee'].search([('user_id', '=', self.user.id)])
        #_logger.info("FONG  SALE empleado: " + str(empleado))
                                                 
            #    """                          
                                                 
        #contador = 1
        #sales = self.env['res.users'].search([('id', '=', '21')])
       # _logger.info("sales: " + str(sales))
     #   self.env.cr.execute("\d res_users")
     #   tipoTabla = str(self.env.cr.fetchall())
     #   _logger.info("query_test: (" + str(tipoTabla)+")")

    
#     _description = 'itl_user_managers.itl_user_managers'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
