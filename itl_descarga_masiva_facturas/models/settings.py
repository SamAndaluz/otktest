from odoo import models, fields, api
from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

class DescargMasivaSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    url_solicitud = fields.Char(string="URL solicitud", help="URL para generar una solicitud de descarga masiva")
    url_estatus = fields.Char(string="URL estatus", help="URL para consultar el estado de la solicitud")
    pfx_file = fields.Binary(string="Archivo PFX", help="Archivo generado con la FIEL del contribuyente")
    filename = fields.Char(string='Nombre archivo')
    password_pfx = fields.Char(string="Contraseña del archivo .pfx")
    contrato = fields.Char(string="Contrato", help="Indica el código de contrato del usuario con el que se realizará la solicitud")
    
    active_cliente = fields.Boolean(string="Descargar facturas cliente", default=False)
    active_proveedor = fields.Boolean(string="Descargar facturas proveedor", default=False)
    
    # Configuración facturas cliente
    cuenta_cobrar_cliente_id = fields.Many2one('account.account',
                                               string='Cuenta por Cobrar Clientes',
                                               required=True, default=lambda self: self.env['account.account'].search(
            [('code', '=', '105.01.001'), ('company_id', '=', self.env.user.company_id.id)]))
    invoice_status_customer = fields.Selection([('draft', 'Borrador'), ('abierta', 'Abierta'), ('pagada', 'Pagada')],
                                               string='Subir en estatus')
    user_customer_id = fields.Many2one('res.users',
                                       string='Representante Comercial')
    team_customer_id = fields.Many2one('crm.team',
                                       string='Equipo de ventas')
    
    # Configuración facturas proveedor
    cuenta_pagar_proveedor_id = fields.Many2one('account.account',
                                                string='Cuenta por Pagar Proveedores',
                                                default=lambda self: self.env['account.account'].search(
            [('code', '=', '201.01.001'), ('company_id', '=', self.env.user.company_id.id)]))
    invoice_status_provider = fields.Selection([('draft', 'Borrador'), ('abierta', 'Abierta'), ('pagada', 'Pagada')],
                                               string='Subir en estatus', required=False)
    warehouse_provider_id = fields.Many2one('stock.warehouse', string='Almacén',
                                            help='Necesario para crear el mov. de almacén', required=False)
    journal_provider_id = fields.Many2one('account.journal',
                                          string='Diario Proveedores',
                                          default=lambda self: self.env['account.journal'].search(
            [('name', '=', 'Vendor Bills'), ('company_id', '=', self.env.user.company_id.id)]))
    user_provider_id = fields.Many2one('res.users', string='Comprador')

    def set_values(self):
        res = super(DescargMasivaSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        
        url_solicitud = self.url_solicitud or False
        url_estatus = self.url_estatus or False
        pfx_file = self.pfx_file or False
        filename = self.filename or False
        password_pfx = self.password_pfx or False
        contrato = self.contrato or False
        active_cliente = self.active_cliente
        active_proveedor = self.active_proveedor
        
        cuenta_cobrar_cliente_id = self.cuenta_cobrar_cliente_id and self.cuenta_cobrar_cliente_id.id or False
        invoice_status_customer = self.invoice_status_customer or False
        user_customer_id = self.user_customer_id and self.user_customer_id.id or False
        team_customer_id = self.team_customer_id and self.team_customer_id.id or False
        
        cuenta_pagar_proveedor_id = self.cuenta_pagar_proveedor_id and self.cuenta_pagar_proveedor_id.id or False
        invoice_status_provider = self.invoice_status_provider or False
        warehouse_provider_id = self.warehouse_provider_id and self.warehouse_provider_id.id or False
        journal_provider_id = self.journal_provider_id and self.journal_provider_id.id or False
        user_provider_id = self.user_provider_id and self.user_provider_id.id or False
        
        param.set_param('itl_descarga_masiva.url_solicitud', url_solicitud)
        param.set_param('itl_descarga_masiva.url_estatus', url_estatus)
        param.set_param('itl_descarga_masiva.pfx_file', pfx_file)
        param.set_param('itl_descarga_masiva.filename', filename)
        param.set_param('itl_descarga_masiva.password_pfx', password_pfx)
        param.set_param('itl_descarga_masiva.contrato', contrato)
        param.set_param('itl_descarga_masiva.active_cliente', active_cliente)
        param.set_param('itl_descarga_masiva.active_proveedor', active_proveedor)
        
        param.set_param('itl_descarga_masiva.cuenta_cobrar_cliente_id', cuenta_cobrar_cliente_id)
        param.set_param('itl_descarga_masiva.invoice_status_customer', invoice_status_customer)
        param.set_param('itl_descarga_masiva.user_customer_id', user_customer_id)
        param.set_param('itl_descarga_masiva.team_customer_id', team_customer_id)
        
        param.set_param('itl_descarga_masiva.cuenta_pagar_proveedor_id', cuenta_pagar_proveedor_id)
        param.set_param('itl_descarga_masiva.invoice_status_provider', invoice_status_provider)
        param.set_param('itl_descarga_masiva.warehouse_provider_id', warehouse_provider_id)
        param.set_param('itl_descarga_masiva.journal_provider_id', journal_provider_id)
        param.set_param('itl_descarga_masiva.user_provider_id', user_provider_id)
        
        return res
    
    @api.model
    def get_values(self):
        res = super(DescargMasivaSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        
        url_solicitud = ICPSudo.get_param('itl_descarga_masiva.url_solicitud')
        url_estatus = ICPSudo.get_param('itl_descarga_masiva.url_estatus')
        pfx_file = ICPSudo.get_param('itl_descarga_masiva.pfx_file')
        filename = ICPSudo.get_param('itl_descarga_masiva.filename')
        password_pfx = ICPSudo.get_param('itl_descarga_masiva.password_pfx')
        contrato = ICPSudo.get_param('itl_descarga_masiva.contrato')
        active_cliente = ICPSudo.get_param('itl_descarga_masiva.active_cliente')
        active_proveedor = ICPSudo.get_param('itl_descarga_masiva.active_proveedor')
        
        cuenta_cobrar_cliente_id = ICPSudo.get_param('itl_descarga_masiva.cuenta_cobrar_cliente_id')
        invoice_status_customer = ICPSudo.get_param('itl_descarga_masiva.invoice_status_customer')
        user_customer_id = ICPSudo.get_param('itl_descarga_masiva.user_customer_id')
        team_customer_id = ICPSudo.get_param('itl_descarga_masiva.team_customer_id')
        
        cuenta_pagar_proveedor_id = ICPSudo.get_param('itl_descarga_masiva.cuenta_pagar_proveedor_id')
        invoice_status_provider = ICPSudo.get_param('itl_descarga_masiva.invoice_status_provider')
        warehouse_provider_id = ICPSudo.get_param('itl_descarga_masiva.warehouse_provider_id')
        journal_provider_id = ICPSudo.get_param('itl_descarga_masiva.journal_provider_id')
        user_provider_id = ICPSudo.get_param('itl_descarga_masiva.user_provider_id')
        
        res.update(
            url_solicitud=url_solicitud,
            url_estatus=url_estatus,
            pfx_file=pfx_file,
            filename=filename,
            contrato=contrato,
            password_pfx=password_pfx,
            cuenta_cobrar_cliente_id=int(cuenta_cobrar_cliente_id),
            invoice_status_customer=invoice_status_customer,
            user_customer_id=int(user_customer_id),
            team_customer_id=int(team_customer_id),
            cuenta_pagar_proveedor_id=int(cuenta_pagar_proveedor_id),
            invoice_status_provider=invoice_status_provider,
            warehouse_provider_id=int(warehouse_provider_id),
            journal_provider_id=int(journal_provider_id),
            user_provider_id=int(user_provider_id),
            active_cliente=active_cliente,
            active_proveedor=active_proveedor
        )
        
        return res