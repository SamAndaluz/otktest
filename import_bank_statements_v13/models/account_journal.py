from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class account_journal_extended(models.Model):
    _inherit = 'account.journal'
    
    import_bank_statement_method = fields.Selection([('banorte','Banorte'),('bancomer_netcash','Bancomer NETCASH'),('santander','Santander'),('mufg_xml_xls','MUFG (xml, xls)'),('mizuho_csv','Mizuho (csv)')], string='Método de carga')
    import_file_name_prefix = fields.Char(string='Prefijo para nombre de archivo')