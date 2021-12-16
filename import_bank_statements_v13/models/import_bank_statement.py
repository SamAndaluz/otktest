# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning
import binascii
from bs4 import BeautifulSoup
import tempfile
import xlrd, re, csv
import pandas as pd
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import io
from datetime import date, datetime
from re import sub
from decimal import Decimal
import xmltodict
from dateutil.parser import parse

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
    

class import_bank_statements(models.TransientModel):
    _name = 'import.bank.statement'
    _description = "Import Bank Statement"
    
    @api.model
    def _default_journal(self):
        journal_type = self.env.context.get('journal_type', False)
        company_id = self.env['res.company']._company_default_get('account.bank.statement').id
        if journal_type:
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                return journals[0]
        return self.env['account.journal']

    
    name = fields.Char(string='Reference')
    #journal_id = fields.Many2one('account.journal', string='Diario', default=_default_journal)
    journal_id = fields.Many2one('account.journal', string='Banco', domain="[('type','=','bank')]", required=True)
    date = fields.Date(string='Fecha',default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', string="Currency")
    
    #bank_name = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['CecobanEmisor']['NombreEmisor'].get('@nombre')
    #account = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@cuenta')
    start_date = fields.Char(string="Starting balance date")
    end_date = fields.Char(string="Ending balance date")
    start_amount = fields.Monetary(string="Starting balance")
    end_amount = fields.Monetary(string="Ending balance")
    
    line_ids = fields.One2many(relation='line_statement_rel', comodel_name='import.bank.statement.line', inverse_name='statement_id', string='Statement lines', domain=[('is_duplicate','=',False)])
    duplicate_line_ids = fields.One2many(relation='duplicate_line_statement_rel', comodel_name='import.bank.statement.line', inverse_name='statement_id', string='Duplicate statement lines', domain=[('is_duplicate','=',True)])
    show_duplicate_lines = fields.Boolean(compute="_check_show_duplicate_lines")
    
    file = fields.Binary(string="Seleccionar archivo")
    file_name = fields.Char(string="Nombre del archivo")
    import_option = fields.Selection([('csv', 'CSV'),('xls', 'XLS'),('xml', 'XML')],string='Tipo', readonly=True)
    
    def _check_show_duplicate_lines(self):
        self.show_duplicate_lines = False
        if len(self.duplicate_line_ids) > 0:
            self.show_duplicate_lines = True
            
    
    #@api.one
    @api.depends('journal_id')
    def _compute_currency(self):
        self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
    
    @api.onchange('file')
    def onchnage_uploaded_file(self):
        if self.file:
            file_ext = self.get_file_ext(self.file_name)
            if file_ext.lower() not in ('csv','xls','xlsx','xml'):
                raise ValidationError('Solo se permiten archivo con extensión csv, xls, xlsx y xml.')
            if file_ext.lower() == 'csv':
                self.import_option = 'csv'
            if file_ext.lower() in ('xls','xlsx'):
                self.import_option = 'xls'
            if file_ext.lower() == 'xml':
                self.import_option = 'xml'
        
    #@api.multi
    def process_file(self):
        lines = []
        self.line_ids = False
        #try:
        if not self.journal_id.import_bank_statement_method:
            self.line_ids = False
            lines = []
            raise ValidationError('El banco seleccionado no tiene registrado un método de carga.')
        if self.journal_id.import_bank_statement_method == 'banorte':
            lines = self.banorte()
        if self.journal_id.import_bank_statement_method == 'bancomer_netcash':
            if not self.journal_id.import_file_name_prefix:
                pass
            else:
                self.validate_bancomer_netcash()
            lines = self.bancomer_netcash()
        if self.journal_id.import_bank_statement_method == 'santander':
            lines = self.santander()
        if self.journal_id.import_bank_statement_method == 'mufg_xml_xls':
            if self.import_option == 'xml':
                lines = self.mufg_xml()
            if self.import_option in ('xls','xlsx','csv'):
                lines = self.mufg_xls()
        if self.journal_id.import_bank_statement_method == 'mizuho_csv':
            lines = self.mizuho_csv()
            _logger.info("### lines: " + str(lines))
        #except Exception as e:
        #    _logger.info("-> error: " + str(e))
        #    raise ValidationError("Error al procesar el archivo: \n" + str(e))
            
        context = self._context.copy()
        if context is None:
            context = {}
        context.update({'lns':lines})
        
        return {
                    'context': context,
                    'name': 'Importar Estados de Cuenta',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'import.bank.statement',
                    'res_id': self.id,
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
    
    def clean_xml(self, xml_string):
        # Este método sirve para remover los caracteres que, en algunos XML, vienen al inicio del string antes del primer
        # caracter '<'
        new_ml_string = xml_string.split('<')
        to_remove = new_ml_string[0]
        new_ml_string = xml_string.replace(to_remove, '')
        # new_ml_string = new_ml_string.replace('&#xA;',' ')
        # new_ml_string = new_ml_string.replace('&quot;','"')

        return new_ml_string
    
    def get_raw_file(self):
        '''Convertir archivo binario a byte string.'''
        return base64.b64decode(self.file)
    
    def mufg_xml(self):
        if self.import_option == 'xml':
            bank_moves = self.get_xml_data_mufg()
            #raise ValidationError(str(bank_moves))
            lines = self.get_values_from_mufg_xml(bank_moves)
            #self.line_ids = lines
            non_duplicate_list, duplicate_list = self.validate_duplicate_lines(lines)
            _logger.info("--> non_duplicate_list: " + str(len(non_duplicate_list)))
            _logger.info("--> duplicate_list: " + str(len(duplicate_list)))
            self.line_ids = non_duplicate_list
            self.duplicate_line_ids = duplicate_list
            
        return lines
    
    def mufg_xls(self):
        lines = False
        if self.import_option == 'xls':
            bank_moves = self.get_xls_data_muf()
            #raise ValidationError(str("OK"))
            lines = self.get_values_from_mufg_xls(bank_moves)
            #self.line_ids = lines
            non_duplicate_list, duplicate_list = self.validate_duplicate_lines(lines)
            _logger.info("--> non_duplicate_list: " + str(len(non_duplicate_list)))
            _logger.info("--> duplicate_list: " + str(len(duplicate_list)))
            self.line_ids = non_duplicate_list
            self.duplicate_line_ids = duplicate_list
            
        return lines
    
    def get_xml_data_mufg(self):
        '''
            Ordena datos de archivo xml
        '''
        #xmls = []
        # convertir byte string a dict
        raw_file = self.get_raw_file()
        xml_string = raw_file.decode('utf-8')
        xml_string = self.clean_xml(xml_string)
        xml = xmltodict.parse(xml_string)

        #xml_file_data = base64.encodestring(file)

        bank_moves = {
            'filename': self.file_name,
            'xml': xml,
            #'xml_file_data': xml_file_data,
        }
        
        return bank_moves
    
    def get_values_from_mufg_xml(self, bank_moves):
        
        if 'comprobantes' not in bank_moves['xml'] and 'cfdi:Comprobante' not in bank_moves['xml']['comprobantes'] and 'cfdi:Addenda' not in bank_moves['xml']['comprobantes']['cfdi:Comprobante'] and 'CecobanEmisor' not in bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda'] and 'btmum:EstadoDeCuentaBTMUM' not in bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']:
            raise ValidationError("El xml seleccionado no tiene movimientos bancarios.")
        
        bank_name = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['CecobanEmisor']['NombreEmisor'].get('@nombre')
        account = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@cuenta')
        account_id = self.env['res.partner.bank'].search([('acc_number','=',account)])[0].id
        start_date = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@fecha_inicial')
        self.start_date = datetime.strptime(start_date, "%Y/%m/%d").strftime('%Y-%m-%d')
        end_date = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@fecha_final')
        self.end_date = datetime.strptime(end_date, "%Y/%m/%d").strftime('%Y-%m-%d')
        start_amount = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@saldo_inicial')
        self.start_amount = float(start_amount)
        end_amount = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM'].get('@saldo_final')
        self.end_amount = float(end_amount)
        
        moves = bank_moves['xml']['comprobantes']['cfdi:Comprobante']['cfdi:Addenda']['btmum:EstadoDeCuentaBTMUM']['btmum:Movimientos']['btmum:Movimiento']
        
        lines = []
        
        for index, move in enumerate(moves):
            index = index + 1
            #if index  == 0:
            #    continue
            
            val = {}
            
            tipo = move.get('@tipo')
            concepto = move.get('@concepto')
            fecha = move.get('@fecha')
            fecha = datetime.strptime(fecha, "%Y/%m/%d").strftime('%Y-%m-%d')
            referencia = move.get('@referencia')
            secuencia = index
            
            if tipo == 'C':
                importe = float(move.get('@importe')) * -1
            else:
                importe = float(move.get('@importe'))
                
            saldo = move.get('@saldo')
            
            if 'RFC' in move.get('@datos_proveedor'):
                datos_proveedor = move.get('@datos_proveedor')
                datos_proveedor = datos_proveedor.split(' ')
                rfc_index = datos_proveedor.index('RFC')
                rfc = datos_proveedor[rfc_index + 2]
                
                rfc = self.elimina_caracteres(rfc)
                            
                if not self.valida_rfc(rfc):
                    continue
                                
                partner_id = self.env['res.partner'].search([('vat','=',rfc)])
                            
                if partner_id:
                    val.update({'partner_id': partner_id[0].id})
                elif 'BENEFICIARIO:' in move.get('@datos_proveedor'):
                    d_p = move.get('@datos_proveedor')
                    bnf_index = datos_proveedor.index('BENEFICIARIO:')
                    nombre_cliente = ''
                    for n in datos_proveedor[bnf_index + 1:]:
                        if '(' in n:
                            break
                        nombre_cliente += n + ' '
                    nombre_cliente = nombre_cliente.strip()
                    vls = {'name': nombre_cliente,
                            'vat': rfc,
                            'is_customer': True}
                            
                    cliente_obj = self.env['res.partner'].sudo()
                    cliente = cliente_obj.create(vls)
                            
                    val.update({'partner_id': cliente.id})
        
            val.update({
                        'sequence': secuencia,
                        'name': concepto,
                        'date': fecha,
                        'ref': referencia,
                        'amount': importe,
                        'bank_account_id': account_id,
                        'cumulative_balance': saldo
                    })
            lines.append((0, 0, val))
 
        return lines
    
    def get_values_from_mufg_xls(self, bank_moves):
        lines = []
        for i in range(len(bank_moves)):
            val = {}
            field = list(map(str, bank_moves[i]))

            if field:
                if i == 0:
                    continue
                else:
                    #raise ValidationError(field[0])
                    account = field[0]
                    account_id = self.env['res.partner.bank'].search([('acc_number','=',account)])[0].id
                    if account_id:
                        val.update({'bank_account_id': account_id})
                        
                    ref = field[3]
                    ref = ref.strip()
                    #if len(account_file) > 0:
                    #    account_file = str(int(field[0]))
                    #if len(ref) > 0:
                    #    ref = str(int(field[8]))
                    
                    account_number = str(self.journal_id.bank_acc_number).strip()
                    
                    if account != account_number:
                        raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                        
                    name = field[7]
                    beneficiario_string_list = ['BEN EFICIARIO:','BENEF ICIARIO:','BENEFICIARIO:','BENEFI CIARIO:','BENE FICIARIO:']
                    words_to_delete = ['BANCO','CLAVE DE RASTREO','CLAVE DE RAST REO','CONCEPTO']
                    beneficiario_found = False
                    bnf_index = False
                    benef_string = False
                    for benef_item in beneficiario_string_list:
                        if benef_item in name:
                            bnf_index = name.index(benef_item)
                            beneficiario_found = True
                            benef_string = benef_item
                            break
                        
                    if beneficiario_found:
                        nombre_cliente = ''
                        for n in name[bnf_index + len(benef_string):]:
                            if ':' in n:
                                break
                            nombre_cliente += n + ''
                        for w_d in words_to_delete:
                            if w_d in nombre_cliente:
                                nombre_cliente = nombre_cliente.replace(w_d, '')
                                break
                        nombre_cliente = nombre_cliente.strip()
                        partner_id = self.env['res.partner'].search([('name','=',nombre_cliente)])
                        if partner_id:
                            partner_id = partner_id[0]
                        if not partner_id:
                            _logger.info("--> partner not found, creating...")
                            vls = {'name': nombre_cliente,
                                    'is_customer': True}

                            cliente_obj = self.env['res.partner'].sudo()
                            partner_id = cliente_obj.create(vls)
                        val.update({'partner_id': partner_id.id})

                    str_date = field[2]
                    format = "%Y-%m-d"
                    #raise ValidationError(str_date)
                    #str_date = datetime.strptime(str_date, format).strftime('%Y-%m-%d')
                    
                    value = field[4]
                    if value != '':
                        val.update({'amount': float(value.replace(',', '')) * -1})
                    
                    value = field[5]
                    if value != '':
                        val.update({'amount': float(value.replace(',', ''))})
                    
                    cum_bal = str(field[6]).replace(',', '')
                        
                    val.update({
                            'name': name,
                            'date': str_date,
                            'ref': ref,
                            'sequence': i,
                            'cumulative_balance': cum_bal
                        })
                    lines.append((0, 0, val))
        return lines
    
    def banorte(self):
        lines = []
        if self.import_option == 'csv':
            file_reader = self.get_csv_data()
            lines = self.get_values_from_csv_data_banorte(file_reader)
            self.line_ids = lines
            
        if self.import_option == 'xls' or self.import_option == 'xlsx':
            sheet = self.get_xls_data()
            lines = self.get_values_from_xls_data_banorte(sheet)
            self.line_ids = lines
            
        if self.import_option == 'xml':
            file_reader = self.get_xml_data()
            lines = self.get_values_from_xml_data(file_reader)
            self.line_ids = lines
            
        return lines
    
    def mizuho_csv(self):
        lines = []
        if self.import_option == 'csv':
            file_reader = self.get_csv_data()
            lines = self.get_values_from_csv_data_mizuho(file_reader)
            non_duplicate_list, duplicate_list = self.validate_duplicate_lines(lines)
            _logger.info("--> non_duplicate_list: " + str(len(non_duplicate_list)))
            _logger.info("--> duplicate_list: " + str(len(duplicate_list)))
            self.line_ids = non_duplicate_list
            self.duplicate_line_ids = duplicate_list
            
    def validate_duplicate_lines(self, lines):
        absl_obj = self.env['account.bank.statement.line']
        non_duplicate_list = []
        duplicate_list = []
        for line in lines:
            line_v = line[2]
            duplicate_line_ids = absl_obj.search([('journal_id','=',self.journal_id.id),('date','=',line_v['date']),('name','ilike',line_v['name']),('amount','=',line_v['amount'])])
            if len(duplicate_line_ids) == 0:
                line[2]['is_duplicate'] = False
                non_duplicate_list.append(line)
            else:
                line[2]['is_duplicate'] = True
                duplicate_list.append(line)
        
        return non_duplicate_list, duplicate_list
            
    
    def santander(self):
        lines = []
        if self.import_option == 'csv':
            file_reader = self.get_csv_data_santander()
            lines = self.get_values_from_csv_data_santander(file_reader)
            self.line_ids = lines
            
        if self.import_option == 'xls' or self.import_option == 'xlsx':
            sheet = self.get_xls_data()
            lines = self.get_values_from_xls_data_santander(sheet)
            self.line_ids = lines
            
        if self.import_option == 'xml':
            file_reader = self.get_xml_data()
            lines = self.get_values_from_xml_data(file_reader)
            self.line_ids = lines
            
        return lines
    
    def get_csv_data(self):
        csv_data = base64.b64decode(self.file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=',')

        try:
            file_reader.extend(csv_reader)
            return file_reader
        except Exception:
            raise Warning(_("Invalid file!"))
    
    def get_csv_data_santander(self):
        csv_data = base64.b64decode(self.file)
        csv_data = str(csv_data, "latin-1")
        file_reader = []
        csv_reader = csv.reader(csv_data.splitlines(), delimiter=',')
        try:
            file_reader.extend(csv_reader)
            return file_reader
        except Exception:
            raise Warning(_("Invalid file!"))
    
    def get_xls_data_muf(self):
        # This is a hack because the xls file has a problem
        csv_data = base64.b64decode(self.file)
        csv_data = str(csv_data, "latin-1")
        file_reader = []
        csv_reader = csv.reader(csv_data.splitlines(), delimiter='\t')
        try:
            file_reader.extend(csv_reader)
            return file_reader
        except Exception:
            raise Warning(_("Invalid file!"))
            
    def get_xls_data(self):
        fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xls")
        fp.write(binascii.a2b_base64(self.file))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        raise ValidationError(workbook)
        sheet = workbook.sheet_by_index(0)
        return sheet

    def get_xml_data(self):
        xml_data = base64.b64decode(self.file)
        data_file = io.StringIO(xml_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = self.read_excel_xml(data_file)
        return file_reader
    
    def get_values_from_csv_data_banorte(self, file_reader):
        lines = []
        for i in range(len(file_reader)):
            val = {}
            field = list(map(str, file_reader[i]))

            if field:
                if i == 0:
                    continue
                else:
                    account_file = self.elimina_caracteres(field[0])
                    account_number = str(self.journal_id.bank_acc_number).strip()
                    if account_file != account_number:
                        raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                    description = field[11]
                    description.upper()
                    if 'RFC' in description:
                        rfc = description[description.find('RFC')+len('RFC'):].split()[0]
                        rfc = self.elimina_caracteres(rfc)
                            
                        if not self.valida_rfc(rfc):
                            continue
                                
                        partner_id = self.env['res.partner'].search([('vat','=',rfc)])
                            
                        if partner_id:
                            val.update({'partner_id': partner_id[0].id})
                        elif 'CLIENTE' in description:
                            strings = description.split(',')
                            matching = [s for s in strings if "CLIENTE" in s][0]
                            nombre_cliente = matching.split('CLIENTE')[1]
                            vls = {'name': nombre_cliente,
                                      'vat': rfc,
                                      'customer': True}
                            
                            cliente_obj = self.env['res.partner'].sudo()
                            cliente = cliente_obj.create(vls)
                            
                            val.update({'partner_id': cliente.id})
                        
                    t_date = datetime.strptime(field[1], "%d/%m/%Y").strftime('%Y-%m-%d')
                        
                    self.date = t_date
                    if str(field[7]).strip() == '-':
                        value = Decimal(sub(r'[^\d.]', '', field[8]))
                        val.update({'amount': value * -1})
                    else:
                        value = Decimal(sub(r'[^\d.]', '', field[7]))
                        val.update({'amount': value})
                    cum_bal = Decimal(sub(r'[^\d.]', '', field[9]))
                        
                    name = ''
                    if str(field[11]).strip() != '-':
                        name = field[11]
                    else:
                        name = field[4]
                    
                    val.update({
                            'name': name,
                            'date': t_date,
                            'ref': field[10],
                            'sequence': i,
                            'cumulative_balance': cum_bal
                        })
                    lines.append((0, 0, val))
        return lines
    
    def is_date(self, string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try: 
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False
    
    def get_values_from_csv_data_mizuho(self, file_reader):
        lines = []
        abs = self.env['account.bank.statement']
        balance_start = abs._get_opening_balance(self.journal_id.id)
        cum_bal = balance_start
        for i in range(len(file_reader)):
            val = {}
            field = list(map(str, file_reader[i]))
            total_lines = len(file_reader)
            if field:
                if i in [0,1,2]:
                    continue
                #if i == 1:
                #    account_name = str(field[8]).split('=')[1]
                #    account_number = str(self.journal_id.bank_acc_number).strip()
                #    _logger.info("--> account_name: " + str(account_name))
                #    _logger.info("--> account_number: " + str(self.journal_id.bank_acc_number))
                #    if account_name != account_number:
                #        raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                else:
                    if not self.is_date(field[0]):
                        break
                    #    cum_bal += float(field[6])
                    if field[3] == 'MSC':
                        #description = field[10] + ' | ' + field[11]
                        description = str(field[10]).strip()
                        """
                        if 'RFC' in description:
                            rfc = description[description.find('RFC')+len('RFC'):].split()[0]
                            rfc = self.elimina_caracteres(rfc)

                            if not self.valida_rfc(rfc):
                                continue

                            partner_id = self.env['res.partner'].search([('vat','=',rfc)])

                            if partner_id:
                                val.update({'partner_id': partner_id[0].id})
                            elif 'CLIENTE' in description:
                                strings = description.split(',')
                                matching = [s for s in strings if "CLIENTE" in s][0]
                                nombre_cliente = matching.split('CLIENTE')[1]
                                vls = {'name': nombre_cliente,
                                          'vat': rfc,
                                          'customer': True}

                                cliente_obj = self.env['res.partner'].sudo()
                                cliente = cliente_obj.create(vls)

                                val.update({'partner_id': cliente.id})
                        """
                        t_date = datetime.strptime(field[0], "%m/%d/%Y").strftime('%Y-%m-%d')

                        self.date = t_date
                        value = 0

                        if str(field[5]).strip() == '':
                            #value = Decimal(sub(r'[^\d.]', '', field[5]))
                            value = float(field[4])
                            val.update({'amount': value * -1})
                            cum_bal = cum_bal - value
                        else:
                            #value = Decimal(sub(r'[^\d.]', '', field[5]))
                            value = float(field[5])
                            val.update({'amount': value})
                            cum_bal = cum_bal + value

                        
                        val.update({
                                'name': description,
                                'date': t_date,
                                'ref': str(field[9]).strip(),
                                'sequence': i,
                                'cumulative_balance': cum_bal
                            })
                        lines.append((0, 0, val))
        return lines
    
    def get_values_from_csv_data_santander(self, file_reader):
        lines = []
        for i in range(len(file_reader)):
            val = {}
            field = list(map(str, file_reader[i]))

            if field:
                if i == 0:
                    continue
                else:
                    #raise ValidationError(int(field[0]))
                    account_file = field[0]
                    account_file = account_file.strip()
                    ref = field[8]
                    ref = ref.strip()
                    if len(account_file) > 0:
                        account_file = str(int(field[0]))
                    if len(ref) > 0:
                        ref = str(int(field[8]))
                    
                    account_number = str(self.journal_id.bank_acc_number).strip()
                    
                    if account_file != account_number:
                        raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                    name = field[4]
                
                    day = str(field[1])[:2]
                    month = str(field[1])[2:4]
                    year = str(field[1])[4:9]
                    str_date = str(int(day))+str(int(month))+year
                    t_date= datetime.strptime(str_date, "%d%m%Y").strftime('%Y-%m-%d')
                    
                    if field[5] == '-':
                        value = field[6]
                        val.update({'amount': float(value) * -1})
                    else:
                        value = field[6]
                        val.update({'amount': value})
                    
                    cum_bal = field[7]
                        
                    val.update({
                            'name': name,
                            'date': t_date,
                            'ref': ref,
                            'sequence': i,
                            'cumulative_balance': cum_bal
                        })
                    lines.append((0, 0, val))
        return lines
    
    def get_values_from_xls_data_banorte(self, sheet):
        lines = []
        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                field = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                account_file = self.elimina_caracteres(field[0])
                account_number = str(self.journal_id.bank_acc_number).strip()
                if account_file != account_number:
                    raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                description = field[11]
                description.upper()
                if 'RFC' in description:
                    rfc = description[description.find('RFC')+len('RFC'):].split()[0]
                    rfc = self.elimina_caracteres(rfc)
                        
                    if not self.valida_rfc(rfc):
                        continue
                            
                    partner_id = self.env['res.partner'].search([('vat','=',rfc)])
                            
                    if partner_id:
                        val.update({'partner_id': partner_id[0].id})
                    elif 'CLIENTE' in description:
                        strings = description.split(',')
                        matching = [s for s in strings if "CLIENTE" in s][0]
                        nombre_cliente = matching.split('CLIENTE')[1]
                        vls = {'name': nombre_cliente,
                                      'vat': rfc,
                                      'customer': True}
                        
                        cliente_obj = self.env['res.partner'].sudo()
                        cliente = cliente_obj.create(vls)
                        
                        val.update({'partner_id': cliente.id})
                        
                t_date= datetime.strptime(field[1], "%d/%m/%Y").strftime('%Y-%m-%d')
                if field[7] == '-':
                    value = Decimal(sub(r'[^\d.]', '', field[8]))
                    val.update({'amount': value * -1})
                else:
                    value = Decimal(sub(r'[^\d.]', '', field[7]))
                    val.update({'amount': value})
                cum_bal = Decimal(sub(r'[^\d.]', '', field[9]))
                    
                name = ''
                if str(field[11]).strip() != '-':
                    name = field[11]
                else:
                    name = field[4]
                        
                val.update({
                            'name': name,
                            'date': t_date,
                            'ref': field[10],
                            'sequence': row_no,
                            'cumulative_balance': cum_bal
                        })
                lines.append((0, 0, val))
        return lines

    def get_values_from_xls_data_santander(self, sheet):
        lines = []
        
        for row_no in range(sheet.nrows):
            val = {}
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                field = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                account_file = self.elimina_caracteres(field[0])
                account_number = str(self.journal_id.bank_acc_number).strip()
                if account_file != account_number:
                    raise ValidationError('El número de cuenta en el archivo no coincide con el número de cuenta del banco seleccionado.')
                name = field[4]
                
                day = str(field[1])[:2]
                month = str(field[1])[2:4]
                year = str(field[1])[4:8]
                str_date = str(int(day))+str(int(month))+year
                t_date= datetime.strptime(str_date, "%d%m%Y").strftime('%Y-%m-%d')
                
                if field[5] == '-':
                    value = field[6]
                    val.update({'amount': float(value) * -1})
                else:
                    value = field[6]
                    val.update({'amount': value})
                    
                cum_bal = field[7]
                        
                val.update({
                            'name': name,
                            'date': t_date,
                            'ref': field[8],
                            'sequence': row_no,
                            'cumulative_balance': cum_bal
                        })
                lines.append((0, 0, val))
        return lines

    def get_values_from_xml_data_bancomer_netcash(self, file_reader):
        lines = []
 
        for i in range(len(file_reader[0])):
            val = {}
            field = list(map(str, file_reader[0][i]))
            
            if field:
                if i == 0:
                    continue
                else:
                    name = field[1]                        
                        
                    t_date = str(field[0]).split('T')[0]
                    t_date = datetime.strptime(t_date, "%Y-%m-%d").strftime('%Y-%m-%d')
                    self.date = t_date
                        
                    if str(field[4]).strip() == '':
                        value = Decimal(sub(r'[^\d.]', '', field[5]))
                        val.update({'amount': value})
                    else:
                        value = Decimal(sub(r'[^\d.]', '', field[4]))
                        val.update({'amount': value * -1})
                    cum_bal = Decimal(sub(r'[^\d.]', '', field[6]))

                    sequence = len(file_reader[0]) - i
                    
                    val.update({
                            'name': name,
                            'date': t_date,
                            'ref': field[3],
                            'sequence': sequence,
                            'cumulative_balance': cum_bal
                        })
                    lines.append((0, 0, val))
        return lines
    
    def bancomer_netcash(self):
        if self.import_option != 'xml':
            raise ValidationError('El banco selecciondado tiene asignado el método de carga Bancomer NETCASH el cual funciona con archivos XML.')
        else:
            file_reader = self.get_xml_data()
            lines = self.get_values_from_xml_data_bancomer_netcash(file_reader)
            #lines.sort(key=lambda tup: tup[2].get('sequence'))
            #raise ValidationError(lines[-1][2].get('name'))
            non_duplicate_list, duplicate_list = self.validate_duplicate_lines(lines)
            _logger.info("--> non_duplicate_list: " + str(len(non_duplicate_list)))
            _logger.info("--> duplicate_list: " + str(len(duplicate_list)))
            self.line_ids = non_duplicate_list
            self.duplicate_line_ids = duplicate_list
            #self.line_ids = lines
        return lines
    
    def read_excel_xml(self, file):
        #file = open(path).read()
        soup = BeautifulSoup(file,'xml')
        workbook = []
        for sheet in soup.findAll('Worksheet'): 
            sheet_as_list = []
            i = 0
            for row in sheet.findAll('Row'):
                row_as_list = []
                if i != 0:
                    for cell in row.findAll('Cell'):
                        row_as_list.append(cell.Data.text)
                    sheet_as_list.append(row_as_list)
                i += 1
            workbook.append(sheet_as_list)
        return workbook
    
    def valida_rfc(self, rfc):
        pattern = '^(([ÑA-Z|ña-z|&]{3}|[A-Z|a-z]{4})\d{2}((0[1-9]|1[012])(0[1-9]|1\d|2[0-8])|(0[13456789]|1[012])(29|30)|(0[13578]|1[02])31)(\w{2})([A|a|0-9]{1}))$|^(([ÑA-Z|ña-z|&]{3}|[A-Z|a-z]{4})([02468][048]|[13579][26])0229)(\w{2})([A|a|0-9]{1})$'
        
        return re.match(pattern, rfc)
    
    def get_month_name(self, start_date, end_date):
        months = {1:'ENERO', 2:'FEBRERO', 3:'MARZO', 4:'ABRIL', 5:'MAYO', 6:'JUNIO', 7:'JULIO', 8:'AGOSTO', 9:'SEPTIEMBRE', 10:'OCTUBRE', 11:'NOVIEMBRE', 12:'DICIEMBRE'}
        month = ''
        if start_date.month == end_date.month:
            month = months.get(start_date.month)
        else:
            month1 = months.get(start_date.month)
            month2 = months.get(end_date.month)
            month = month1+','+month2
        
        return month
    
    #@api.multi
    def import_statements_new(self):
        if not self.line_ids:
            raise ValidationError('Primero debe de procesar un archivo.')
        acc_stmt = self.env['account.bank.statement']
        
        if self.journal_id.import_bank_statement_method == 'mufg_xml':
            name, bank_statement = self.validate_statement_mufg()
        else:
            name, bank_statement = self.validate_statement(acc_stmt)
        
        lines = self.get_new_data()
        
        last_bnk_stmt = acc_stmt.search([('journal_id', '=', self.journal_id.id)], limit=1)
        if bank_statement:
            if bank_statement.id != last_bnk_stmt.id:
                raise ValidationError('Parece ser que el extracto bancario que desea subir no es consecutivo en fecha del útimo extracto bancario en el sistema.')
        
        lst_bnk_dates = last_bnk_stmt.line_ids.mapped('date')
        lst_bnk_ref = last_bnk_stmt.line_ids.mapped('ref')
        lst_bnk_amount = last_bnk_stmt.line_ids.mapped('amount')
        tuple_1 = list(zip(lst_bnk_dates, lst_bnk_ref, lst_bnk_amount))
        
        line_dates = [l[2].get('date') for l in lines]
        line_ref = [l[2].get('ref') for l in lines]
        line_amount = [l[2].get('amount') for l in lines]
        tuple_2 = list(zip(line_dates, line_ref, line_amount))
        
        unmatched = set(tuple_2) - set(tuple_1)
        unmatched = list(unmatched)
        #raise ValidationError(str(unmatched))
        if len(unmatched) == 0:
            unmatched = set(tuple_1) & set(tuple_2)
            unmatched = list(unmatched)
            #raise ValidationError(str(unmatched))
        
        
        
        um_date = list(map(lambda x: x[0], unmatched))
        um_ref = list(map(lambda x: x[1], unmatched))
        um_amount = list(map(lambda x: x[2], unmatched))
        
        lines_new = [l for l in lines if l[2].get('date') in um_date and l[2].get('ref') in um_ref and l[2].get('amount') in um_amount]
        
        if len(lines_new) > 0:
            result = acc_stmt.search([('name','=',name)])
            if len(result) > 0:
                name = name + ' ' + str(len(lines_new) + 1)
        else:
            lines_new = lines
        
        if self.journal_id.import_bank_statement_method == 'mufg_xml_xls':
            
            if self.import_option == 'xml':
                new_lines = []
                for l in lines_new:
                    l[2].pop('cumulative_balance')
                    new_lines.append(l)
                acc_stmt_created = acc_stmt.with_context(journal_id=self.journal_id.id).create({
                        'journal_id': self.journal_id.id,
                        'name': name,
                        'line_ids': new_lines,
                        'balance_start': self.start_amount,
                        'balance_end_real': self.end_amount
                    })
            if self.import_option == 'xls':
                balance_start = 0
                balance_end_real = lines_new[-1][2].get('cumulative_balance')
                #raise ValidationError(str(balance_end_real))
                if last_bnk_stmt:
                    balance_start = last_bnk_stmt.balance_end
                else:
                    balance_start = float(balance_end_real) - (float(lines_new[-1][2].get('amount')))
                new_lines = []
                for l in lines_new:
                    l[2].pop('cumulative_balance')
                    new_lines.append(l)
                acc_stmt_created = acc_stmt.with_context(journal_id=self.journal_id.id).create({
                    'journal_id': self.journal_id.id,
                    'name': name,
                    'line_ids': new_lines,
                    'balance_start': balance_start,
                    'balance_end_real': balance_end_real
                })
            
        else:
            balance_start = 0
            balance_end_real = lines_new[-1][2].get('cumulative_balance')
            if last_bnk_stmt:
                balance_start = last_bnk_stmt.balance_end
            else:
                balance_start = float(balance_end_real) + (float(lines_new[0][2].get('amount')) * -1)
            new_lines = []
            for l in lines_new:
                l[2].pop('cumulative_balance')
                new_lines.append(l)
            acc_stmt_created = acc_stmt.with_context(journal_id=self.journal_id.id).create({
                'journal_id': self.journal_id.id,
                'name': name,
                'line_ids': lines_new,
                'balance_start': balance_start,
                'balance_end_real': balance_end_real
            })
        
        return {
                    'context': self.env.context,
                    'name': 'Extractos bancarios',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.bank.statement',
                    'res_id': acc_stmt_created.id,
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }

    def get_new_data(self):
        val = {}
        lines = []
        #raise ValidationError(self.line_ids[0].sequence)
        for r in self.line_ids:
            val.update({
                        'name': r.name,
                        'date': r.date,
                        'partner_id': r.partner_id.id,
                        'ref': r.ref,
                        'sequence': r.sequence,
                        'amount': r.amount,
                        'bank_account_id': r.bank_account_id.id,
                        'cumulative_balance': r.cumulative_balance
                        })
            lines.append((0, 0, val))
            val = {}
        lines.sort(key=lambda tup: tup[2].get('sequence'))
        #raise ValidationError(lines[0][2].get('name'))
        return lines
    
    def elimina_caracteres(self, name):
        new_name = name.strip()
        new_name = re.sub('[*"<>\/.,?:| ]', '', new_name)
        new_name = new_name.replace("\\", "")
        new_name = new_name.replace("'", "")
        
        return new_name

    def get_file_ext(self,filename):
        """
        obtiene extencion de archivo, si este lo tiene
        fdevuelve false, si no cuenta con una aextension
        (no es archivo entonces)
        """
        file_ext = filename.split('.')
        if len(file_ext) > 1:
            file_ext = filename.split('.')[1]
            return file_ext
        return False
    
    def validate_bancomer_netcash(self):
        prefijo = self.journal_id.import_file_name_prefix.strip().replace(" ", "").lower()
        file_name = self.file_name.strip().replace(" ","").lower()
        if not file_name.startswith(prefijo):
            raise ValidationError('El nombre del archivo no contiene el prefijo configurado en el banco seleccionado.')
    
    def validate_statement(self, acc_stmt):
        start_date = self.line_ids[0].date
        end_date = self.line_ids[-1].date
        month = self.get_month_name(start_date, end_date)
        
        name = str(self.journal_id.name) + ' ' + month + ' ' + str(start_date.day) + '-' + str(end_date.day) + ' ' + str(self.date.year)
        
        if ',' in month:
            months = month.split(',')
            name = str(self.journal_id.name) + ' ' + months[0] + ' ' + str(start_date.day) + ' - ' + months[1] + ' ' + str(end_date.day) + ' ' + str(self.date.year)
        
        if start_date == end_date:
            name = str(self.journal_id.name) + ' ' + month + ' ' + str(end_date.day) + ' ' + str(self.date.year)
        if end_date < start_date:
            name = str(self.journal_id.name) + ' ' + month + ' ' + str(end_date.day) + '-' + str(start_date.day) + ' ' + str(self.date.year)
        
        #result = acc_stmt.search([('name','=',name)])
        #if len(result) > 0:
        #    raise ValidationError('Ya existe un extracto bancario con el mismo nombre %s.' % name)

        bank_statements = self.env['account.bank.statement'].search([('journal_id','=',self.journal_id.id)])
        
        bank_statements = bank_statements.filtered(lambda r: start_date >= list(dict.fromkeys(r.line_ids.mapped('date')))[0] and start_date <= list(dict.fromkeys(r.line_ids.mapped('date')))[-1] or end_date >= list(dict.fromkeys(r.line_ids.mapped('date')))[0] and end_date <= list(dict.fromkeys(r.line_ids.mapped('date')))[-1])
        
        if len(bank_statements) > 0:
            #raise ValidationError(bank_statements)
            #raise ValidationError('Parece ser que algunas de las fechas del extracto bancario que desea cargar ya existen en algún extracto bancario del sistema.')
            return name, bank_statements[0]
        
        return name, bank_statements
    
    def validate_statement_mufg(self):
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d").date()
        
        month = self.get_month_name(start_date, end_date)
        
        name = str(self.journal_id.name) + ' ' + month + ' ' + str(start_date.day) + '-' + str(end_date.day) + ' ' + str(self.date.year)
        
        if ',' in month:
            months = month.split(',')
            name = str(self.journal_id.name) + ' ' + months[0] + ' ' + str(start_date.day) + ' - ' + months[1] + ' ' + str(end_date.day) + ' ' + str(self.date.year)
        
        if start_date == end_date:
            name = str(self.journal_id.name) + ' ' + month + ' ' + str(end_date.day) + ' ' + str(self.date.year)
        if end_date < start_date:
            name = str(self.journal_id.name) + ' ' + month + ' ' + str(end_date.day) + '-' + str(start_date.day) + ' ' + str(self.date.year)
        
        bank_statements = self.env['account.bank.statement'].search([('journal_id','=',self.journal_id.id)])
        #raise ValidationError(str(start_date) + ' - ' + str(lambda r: start_date >= list(dict.fromkeys(r.line_ids.mapped('date')))[0]))
        bank_statements = bank_statements.filtered(lambda r: start_date >= list(dict.fromkeys(r.line_ids.mapped('date')))[0] and start_date <= list(dict.fromkeys(r.line_ids.mapped('date')))[-1] or end_date >= list(dict.fromkeys(r.line_ids.mapped('date')))[0] and end_date <= list(dict.fromkeys(r.line_ids.mapped('date')))[-1])
        
        if len(bank_statements) > 0:
            return name, bank_statements[0]
        
        return name, bank_statements
    
class import_bank_statements(models.TransientModel):
    _name = 'import.bank.statement.line'
    _description = "Import Bank Statement Line"
    _order = 'sequence desc'
    
    statement_id = fields.Many2one('import.bank.statement', string='Statement', ondelete='cascade')
    
    name = fields.Char(string='Etiqueta')
    date = fields.Date(string='Fecha', default=lambda self: self._context.get('date', fields.Date.context_today(self)), readonly=True)
    partner_id = fields.Many2one('res.partner', string='Cliente/Proveedor')
    ref = fields.Char(string='Referencia')
    journal_currency_id = fields.Many2one('res.currency', string="Journal's Currency", related='statement_id.currency_id')
    amount = fields.Monetary(digits=0, currency_field='journal_currency_id', string='Cantidad', readonly=True)
    sequence = fields.Integer(default=1, readonly=True)
    bank_account_id = fields.Many2one('res.partner.bank', string="Bank account")
    cumulative_balance = fields.Monetary(digits=0, currency_field='journal_currency_id')
    is_duplicate = fields.Boolean()