# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from urllib.request import urlopen
import urllib
import requests
import json
import base64
import pytz
from pytz import timezone


import logging
_logger = logging.getLogger(__name__)


class ItlRequests(models.Model):
    _name = "itl.request"
    _inherit = ['mail.thread']
    _rec_name = "id"
    
    def _get_pfx_b64(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        pfx_file = ICPSudo.get_param('itl_descarga_masiva.pfx_file') or False
        
        if pfx_file:
            return pfx_file
    
    def _get_usuario_pade(self):
        user_name = self.env.company.l10n_mx_edi_pac_username
        if user_name:
            return user_name
    
    def _get_pass_pade(self):
        password = self.env.company.l10n_mx_edi_pac_password
        if password:
            return password
        
    def _get_password_pfx(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        password_pfx = ICPSudo.get_param('itl_descarga_masiva.password_pfx') or False
        
        if password_pfx:
            return password_pfx
    
    def _get_contrato(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        contrato = ICPSudo.get_param('itl_descarga_masiva.contrato') or False
        
        if contrato:
            return contrato
    
    # Request inicial
    tipoFactura = fields.Selection([('cliente','Cliente'),('proveedor','Proveedor')], string="Tipo de factura", required=True)
    rfcEmisor = fields.Char(string="RFC Emisor")
    rfcReceptor = fields.Char(string="RFC Receptor")
    rfcSolicitante = fields.Char(string="RFC Solicitante", required=True, default=lambda self: self.env.company.vat)
    fechaInicio = fields.Datetime(string="Fecha inicio", required=True, default=fields.Datetime.today)
    fechaFinal = fields.Datetime(string="Fecha final", required=True, default=fields.Datetime.today)
    tipoSolicitud = fields.Selection([('CFDI','CFDI'),('Metadata','Metadata')], string="Tipo de solicitud", required=True)
    pfx = fields.Text(string="PFX (base64)", required=True, default=_get_pfx_b64)
    password = fields.Char(string="Contraseña PFX", required=True, default=_get_password_pfx)
    usuario = fields.Char(string="Usuario PADE", required=True, default=_get_usuario_pade)
    passPade = fields.Char(string="Contraseña PADE", required=True, default=_get_pass_pade)
    contrato = fields.Char(string="Contrato", required=True, default=_get_contrato)
    numeroSolicitud = fields.Char(string="Número de solicitud")
    response_ids = fields.One2many('itl.response', 'id_request', string="Responses")
    status = fields.Selection([('nueva','Nueva'),('generada','Generada'),('lista','Lista'),('terminada','Terminada')], string="Estado", default='nueva')
    invoice_ids = fields.Char(string="Invoice ids")
    
    
    @api.onchange('tipoFactura')
    def _onchnage_tipoFactura(self):
        if self.tipoFactura:
            if self.tipoFactura == 'cliente':
                self.rfcEmisor = self.env.company.vat
                self.rfcReceptor = False
            if self.tipoFactura == 'proveedor':
                self.rfcReceptor = self.env.company.vat
                self.rfcEmisor = False
    
    def nueva_solicitud(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        active_cliente = ICPSudo.get_param('itl_descarga_masiva.active_cliente')
        active_proveedor = ICPSudo.get_param('itl_descarga_masiva.active_proveedor')
        
        if active_cliente:
            self.crear_solicitud('cliente')
        if active_proveedor:
            self.crear_solicitud('proveedor')
    
    def crear_solicitud(self, tipoFactura=None):
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_tz = pytz.UTC.localize(datetime.strptime(str(fields.Datetime.now()), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(timezone('America/Mexico_City'))
        
        only_date = date_tz.strftime("%Y-%m-%d")
        _logger.info("---> only_date: " + str(only_date))
        local = pytz.timezone ("America/Mexico_City")
        combineInicio = datetime.strptime(only_date + str(' 00:00:02'), '%Y-%m-%d %H:%M:%S')
        local_dt = local.localize(combineInicio, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        fechaInicio = datetime.strftime(utc_dt - timedelta(1), '%Y-%m-%d %H:%M:%S')
        
        combineFin = datetime.strptime(only_date + str(' 23:59:58'), '%Y-%m-%d %H:%M:%S')
        local_dt = local.localize(combineFin, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        fechaFinal = datetime.strftime(utc_dt - timedelta(1), '%Y-%m-%d %H:%M:%S')
        
        params = {
            "rfcSolicitante": self.env.company.vat,
            "fechaInicio": fechaInicio,
            "fechaFinal": fechaFinal,
            "tipoSolicitud": 'CFDI',
            "pfx": self._get_pfx_b64(),
            "password": self._get_password_pfx(),
            "usuario": self._get_usuario_pade(),
            "passPade": self._get_pass_pade(),
            "contrato": self._get_contrato(),
            "status": 'nueva'
        }
        #_logger.info(str("---> params: ") + str(params))
        if tipoFactura:
            if tipoFactura == 'cliente':
                if self.env.company.vat:
                    params.update({"rfcEmisor": self.env.company.vat,
                                  "tipoFactura": tipoFactura})
            if tipoFactura == 'proveedor':
                if self.env.company.vat:
                    params.update({"rfcReceptor": self.env.company.vat,
                                  "tipoFactura": tipoFactura})
        else:
            if self.tipoFactura == 'cliente':
                if self.env.company.vat:
                    params.update({"rfcEmisor": self.env.company.vat})
            if self.tipoFactura == 'proveedor':
                if self.env.company.vat:
                    params.update({"rfcReceptor": self.env.company.vat})
        
        res = all(params.values())
        if not res:
            _logger.info(str("Hay algunos campos vacíos en el cuerpo de la solicitud."))
            self.message_post(body="Solicitud no generada. Hay algunos campos vacíos en el cuerpo de la solicitud.", subject="Error al generar la solicitud")
            #_logger.info(str(params))
        else:
            #_logger.info(str("Cuerpo de la solicitud"))
            #_logger.info(str(params))
            
            record = self.create(params)
            #raise ValidationError("Testing...")
            _logger.info(str("Registro creado"))
            record.generar_solicitud()
            
    
    def generar_solicitud(self):
        if self.status == 'nueva':
            self.validations()
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url_solicitud = ICPSudo.get_param('itl_descarga_masiva.url_solicitud') or False

            #convert the date string into object 
            fechaInicio = self.fechaInicio.strftime("%Y-%m-%dT%H:%M:%S")
            utc_start_date = datetime.strptime(fechaInicio,"%Y-%m-%dT%H:%M:%S")
            fechaInicio = utc_start_date.astimezone(timezone('America/Mexico_City'))
            fechaInicio = fechaInicio.strftime("%Y-%m-%dT%H:%M:%S")

            fechaFinal = self.fechaFinal.strftime("%Y-%m-%dT%H:%M:%S")
            utc_end_date = datetime.strptime(fechaFinal,"%Y-%m-%dT%H:%M:%S")
            fechaFinal = utc_end_date.astimezone(timezone('America/Mexico_City'))
            fechaFinal = fechaFinal.strftime("%Y-%m-%dT%H:%M:%S")

            params = {
                "rfcSolicitante": self.rfcSolicitante,
                "fechaInicio": fechaInicio,
                "fechaFinal": fechaFinal,
                "tipoSolicitud": self.tipoSolicitud,
                "pfx": self.pfx,
                "password": self.password,
                "usuario": self.usuario,
                "passPade": self.passPade,
                "contrato": self.contrato,
            }
            
            if self.tipoFactura == 'cliente':
                if self.env.company.vat:
                    params.update({"rfcEmisor": self.rfcEmisor})
            if self.tipoFactura == 'proveedor':
                if self.env.company.vat:
                    params.update({"rfcReceptor": self.rfcReceptor})


            headers = {'Content-type': 'application/json'}
            try:
                r = requests.post(url_solicitud, data=json.dumps(params),  headers=headers, verify=False)
                if r.status_code not in [200, 201, 202, 203, 204]:
                    self.message_post(body="Ocurrió un error en la llamada a la API que genera la solicitud. Error: " + str(r) + " Code: " + str(r.status_code), subject="Error en llamada a API")
                    return
                data = r.json() 
                #raise ValidationError(str(data))
                values = {
                    'id_request': self.id
                }

                if 'numeroSolicitud' in data:
                    values.update(
                        {'numeroSolicitud': data['numeroSolicitud'],
                         'estadoSolicitud': data['estadoSolicitud'],
                         'mensaje': data['mensaje'][0]
                        })
                    if data['numeroSolicitud'] != "0":
                        self.numeroSolicitud = data['numeroSolicitud']
                        self.status = 'generada'
                    else:
                        self.message_post(body="Solicitud no generada. " + str(data['mensaje'][0]), subject="Solicitud no generada")
                    if 'respuestaSAT' in data:
                        values.update({'respuestaSAT': data['respuestaSAT']})
                if 'apierror' in data:
                    values.update({
                        'estadoSolicitud': data['status'],
                        'mensaje': data['message'] + " código: " + str(data['codigo'])
                    })

                self.response_ids = [(0, 0, values)]
                if self.tipoFactura == 'cliente':
                    self.message_post(body="Solicitud para descarga de facturas de cliente generada correctamente.", subject="Solicitud generada")
                if self.tipoFactura == 'proveedor':
                    self.message_post(body="Solicitud para descarga de facturas de proveedor generada correctamente.", subject="Solicitud generada")
            except requests.exceptions.RequestException as e:
                self.message_post(body="Ocurrió un error en la llamada a la API que genera la solicitud. " + str(e), subject="Error en llamada a API")
            
    def revisa_solicitudes(self):
        _logger.info(str("Revisando el estado de las solicitudes"))
        solicitudes = self.search([('status','=','generada')])
        
        if solicitudes:
            for solicitud in solicitudes:
                solicitud.estado_solicitud()
            _logger.info(str("Fin de la revisión"))
        else:
            _logger.info(str("Ninguna solicitud por revisar"))
    
    def estado_solicitud(self):
        if self.status in ['generada','terminada']:
            _logger.info(str("Solicitud #: " + str(self.id)))
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url_estatus = ICPSudo.get_param('itl_descarga_masiva.url_estatus') or False

            params = {
                "numeroSolicitud": self.numeroSolicitud,
                "usuario": self.usuario,
                "passPade": self.passPade,
                "contrato": self.contrato,
            }

            headers = {'Content-type': 'application/json'}
            try:
                r = requests.post(url_estatus, data=json.dumps(params), headers=headers, verify=False)
                if r.status_code not in [200, 201, 202, 203, 204]:
                    self.message_post(body="Ocurrió un error en la llamada a la API que genera la solicitud. Error: " + str(r) + " Code: " + str(r.status_code), subject="Error en llamada a API")
                    return
                data = r.json() 

                values = {
                    'id_request': self.id
                }

                if 'numeroSolicitud' in data:
                    values.update(
                        {'numeroSolicitud': data['numeroSolicitud'],
                         'estadoSolicitud': data['estadoSolicitud'],
                         'mensaje': data['mensaje'][0]
                        })
                    if 'paquetes' in data:
                        values.update({'paquetes': data['paquetes'][0]})
                        self.status = 'lista'
                        self.response_ids = [(0, 0, values)]
                        self.message_post(body="Paquetes listos para descargar.", subject="Descarga lista")
                        self.obtener_paquetes()
                    elif 'estadoSolicitud' in data and data['estadoSolicitud'] == "5":
                        self.status = 'terminada'
                        self.response_ids = [(0, 0, values)]
                    else:
                        self.response_ids = [(0, 0, values)]
            except requests.exceptions.RequestException as e:
                self.message_post(body="Ocurrió un error en la llamada a la API que obtiene el estado de la solicitud. " + str(e), subject="Error en llamada a API")

            
    def obtener_paquetes(self):
        if self.response_ids:
            responses = self.response_ids.filtered(lambda r: r.estadoSolicitud == "7" and r.paquetes)
            if responses:
                _logger.info(str("Paquetes URL: " + str(responses[-1].paquetes)))
                try:
                    _logger.info("Descargando paquetes...")
                    paquetes = urlopen(responses[-1].paquetes).read()
                    paquetes_b64_encoded = base64.b64encode(paquetes)
                    paquetes_b64 = paquetes_b64_encoded.decode('utf-8')
                    _logger.info("Paquetes descargados...")
                    if self.tipoSolicitud == 'CFDI':
                        self.importar_facturas(paquetes_b64)
                    else:
                        filename = responses[-1].paquetes.split('?')[0].split('/')[-1] + ".zip"
                        self.attach_to_solicitud(self, paquetes_b64_encoded, filename)
                        self.message_post(body="Archivo de metadatos descargado y adjuntado correctamente.", subject="Archivo de metadata listo")
                        self.status = 'terminada'
                    
                except urllib.error.URLError as e:
                    self.message_post(body="Error durante la descarga: " + str(e.reason) + " code: " + str(e.code), subject="Error en descarga")
                    _logger.info("Error durante la descarga: " + str(e.reason) + " code: " + str(e.code))
    
    def attach_to_solicitud(self, solicitud, zip_file, paquete_name):
        sub_values = {
            'res_model': 'itl.request',
            'res_id': solicitud.id,
            #'name': invoice.l10n_mx_edi_cfdi_name,
            'name': paquete_name,
            'datas': zip_file,
            #'datas_fname': xml_name,
        }
        IrAttachment = self.env['ir.attachment'].sudo()
        
        attachment = IrAttachment.create(sub_values)
        
        return attachment
    
    def get_raw_file(self, paquetes_b64):
        '''Convertir archivo binario a byte string.'''
        return base64.b64decode(paquetes_b64)
    
    def ver_invoices(self):
        view = 'account.action_move_in_invoice_type'
        #view = 'account.action_invoice_tree2'
        action = self.env.ref(view).read()[0]
        invoice_ids = json.loads(self.invoice_ids)
        action['domain'] = [('id', 'in', invoice_ids)]
        return action  
                    
    def importar_facturas(self, paquetes):
        import_obj = self.env['xml.import.wizard']
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        #Config for client
        cuenta_cobrar_cliente_id = ICPSudo.get_param('itl_descarga_masiva.cuenta_cobrar_cliente_id') or False
        cuenta_cobrar_cliente_id = self.env['account.account'].browse(int(cuenta_cobrar_cliente_id))
        invoice_status_customer = ICPSudo.get_param('itl_descarga_masiva.invoice_status_customer') or False
        user_customer_id = ICPSudo.get_param('itl_descarga_masiva.user_customer_id') or False
        user_customer_id = self.env['res.users'].browse(int(user_customer_id))
        team_customer_id = ICPSudo.get_param('itl_descarga_masiva.team_customer_id') or False
        team_customer_id = self.env['crm.team'].browse(int(team_customer_id))
        
        #Config for provider
        cuenta_pagar_proveedor_id = ICPSudo.get_param('itl_descarga_masiva.cuenta_pagar_proveedor_id') or False
        cuenta_pagar_proveedor_id = self.env['account.account'].browse(int(cuenta_pagar_proveedor_id))
        invoice_status_provider = ICPSudo.get_param('itl_descarga_masiva.invoice_status_provider') or False
        warehouse_provider_id = ICPSudo.get_param('itl_descarga_masiva.warehouse_provider_id') or False
        warehouse_provider_id = self.env['stock.warehouse'].browse(int(warehouse_provider_id))
        journal_provider_id = ICPSudo.get_param('itl_descarga_masiva.journal_provider_id') or False
        journal_provider_id = self.env['account.journal'].browse(int(journal_provider_id))
        user_provider_id = ICPSudo.get_param('itl_descarga_masiva.user_provider_id') or False
        user_provider_id = self.env['res.users'].browse(int(user_provider_id))
        
        vals = {
            'cuenta_cobrar_cliente_id': cuenta_cobrar_cliente_id.id,
            'invoice_status_customer': invoice_status_customer,
            'user_customer_id': user_customer_id.id,
            'team_customer_id': team_customer_id.id,
            'cuenta_pagar_proveedor_id': cuenta_pagar_proveedor_id.id,
            'invoice_status_provider': invoice_status_provider,
            'warehouse_provider_id': warehouse_provider_id.id,
            'journal_provider_id': journal_provider_id.id,
            'user_provider_id': user_provider_id.id,
            'uploaded_file': paquetes
        }
        record = import_obj.create(vals)
        
        invoice_ids, mensaje2 = record.validate_bills_downloaded()
        
        if invoice_ids:
            invoice_list = []
            if self.invoice_ids:
                invoice_list = self.invoice_ids.strip('][').split(', ')
                invoice_list = list(map(int, invoice_list)) 
            self.invoice_ids = invoice_ids + invoice_list
            self.message_post(body="Facturas descargadas e importadas correctamente.", subject="Importación correcta")
        
        if mensaje2:
            self.message_post(body=mensaje2, subject="Log de importación")
            
        self.status = 'terminada'
    
    def get_raw_file(self, pfx_file):
        '''Convertir archivo binario a byte string.'''
        return base64.b64decode(pfx_file)

    def validations(self):
        if self.tipoFactura == 'cliente':
            if not self.rfcEmisor:
                self.message_post(body="No se ha establecido el RFC de la compañía", subject="Problema con RFC")
        if self.tipoFactura == 'proveedor':
            if not self.rfcReceptor:
                self.message_post(body="No se ha establecido el RFC de la compañía", subject="Problema con RFC")
        if not self.pfx:
            self.message_post(body="Debe de colocar el archivo PFX en la configuración", subject="Problema con archivo PFX")
        if self.fechaInicio > self.fechaFinal:
            self.message_post(body="El rango de fechas es incorrecto", subject="Problema con fechas")
            
    
class ItlResponse(models.Model):
    _name = "itl.response"
    
    id_request = fields.Many2one('itl.request', string="Request", ondelete='cascade')

    numeroSolicitud = fields.Char(string="Número de solicitud")
    estadoSolicitud = fields.Char(string="Estado de la solicitud")
    mensaje = fields.Char(string="Mensaje")
    respuestaSAT = fields.Char(string="Respuesta SAT")
    paquetes = fields.Char(string="Paquetes")