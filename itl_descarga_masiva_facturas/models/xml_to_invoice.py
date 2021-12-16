
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class XmlImportWizard(models.TransientModel):
    _inherit = 'xml.import.wizard'
    
    
    def validate_bills_downloaded(self):
        '''
            Función principal. Controla todo el flujo de
            importación al clickear el botón (parsea el archivo
            subido, lo valida, obtener datos de la factura y
            guardarla crea factura en estado de borrador).
        '''

        raw_file = self.get_raw_file()
        zip_file = self.get_zip_file(raw_file)

        if zip_file:

            # extraer archivos dentro del .zip
            bills = self.get_xml_from_zip(zip_file)
            #raise ValidationError(str(bills))
        else:
            bills = self.get_xml_data(raw_file)
        
        valid_bills = []
        invalid_bills = []
        for bill in bills:
            mensaje = self.validations(bill)
            if mensaje:
                invalid_bills.append(mensaje)
                continue
            #raise ValidationError('ccccc')
            invoice, invoice_line, version, invoice_type, bank_id = self.prepare_invoice_data(bill)

            bill['bank_id'] = bank_id
            bill['invoice_type'] = invoice_type
            bill['invoice_data'] = invoice
            bill['invoice_line_data'] = invoice_line
            bill['version'] = version
            bill['valid'] = True

            mensaje = self.validations(bill)
            if mensaje:
                invalid_bills.append(mensaje)
                continue

            valid_bills.append(bill)

        # si todos son válidos, extraer datos del XML
        # y crear factura como borrador
        invoice_ids = []
        invoices_no_created = []
        warning_bills = []
        mensaje3 = ''
        for bill in valid_bills:
            invoice = bill['invoice_data']
            invoice_line = bill['invoice_line_data']
            invoice_type = bill['invoice_type']
            version = bill['version']
            
            if invoice_type == 'out_invoice' or invoice_type == 'out_refund':
                #_logger.info("invoice: " + str(invoice))
                draft, mensaje = self.create_bill_draft(invoice, invoice_line, invoice_type)
            else:
                draft, mensaje = self.create_bill_draft_vendor(invoice, invoice_line, invoice_type)

            #draft.compute_taxes()
            #raise ValidationError(str(draft.state))
            # se asigna diario
            draft.journal_id = invoice['journal_id']
            #draft.account_id = invoice['account_id']

            # se adjunta xml
            #raise ValidationError(str(self.env['account.move'].search_read([('id','=',draft.id)],[])) + "\n\n" + str(bill['xml_file_data']) + "\n\n" + str(bill['filename']))
            self.attach_to_invoice(draft, bill['xml_file_data'], bill['filename'])
            
            draft.l10n_mx_edi_cfdi_name = bill['filename']

            if invoice_type == 'out_invoice' or invoice_type == 'out_refund':
                #draft.l10n_mx_edi_payment_method_id = self.payment_method_customer
                #draft.l10n_mx_edi_usage = self.usage_customer

                if self.invoice_status_customer == 'abierta':
                    # se valida factura
                    draft.payment_term_id = self.payment_term_customer_id
                    #draft.action_invoice_open()
                    draft.action_post()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                ### Paga factura cliente
                if self.invoice_status_customer == 'pagada':
                    if draft.partner_id.property_payment_term_id:
                        draft.payment_term_id = draft.partner_id.property_payment_term_id
                    else:
                        if self.invoice_payment_type_customer == 'fecha_fin_mes':
                            year = datetime.now().year
                            month = datetime.now().month
                            day = calendar.monthrange(year, month)[1]
                            draft.date_invoice = datetime(year, month, day).date()
                        if self.invoice_payment_type_customer == 'fecha_especifica':
                            if not draft.date_invoice < self.invoice_date_customer:
                                draft.date_invoice = self.invoice_date_customer

                    #draft.action_invoice_open()
                    draft.action_post()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                    # si el termino de pago es contado, se valida la factura y se paga
                    # (solo para facturas de venta)

                    if self.is_immediate_term(draft.payment_term_id):
                        # Pago inmediato
                        draft.payment_term_id = 13
                        # SE CREA PAGO DE FACTURA
                        payment = self.create_payment(draft, bill['bank_id'])
                        payment.post()
            else:
                ### Abierta factura proveedor
                if self.invoice_status_provider == 'abierta':
                    # se valida factura
                    draft.payment_term_id = self.payment_term_provider_id
                    #draft.action_invoice_open()
                    draft.action_post()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'
                ### Paga factura proveedor
                if self.invoice_status_provider == 'pagada':
                    if draft.partner_id.property_payment_term_id:
                        draft.payment_term_id = draft.partner_id.property_payment_term_id
                    else:
                        if self.invoice_payment_type_provider == 'fecha_fin_mes':
                            year = datetime.now().year
                            month = datetime.now().month
                            day = calendar.monthrange(year, month)[1]
                            draft.date_invoice = datetime(year, month, day).date()
                        if self.invoice_payment_type_provider == 'fecha_especifica':
                            if not draft.date_invoice < self.invoice_date_provider:
                                draft.date_invoice = self.invoice_date_provider

                    #draft.action_invoice_open()
                    draft.action_post()
                    draft.l10n_mx_edi_pac_status = 'signed'
                    draft.l10n_mx_edi_sat_status = 'valid'

                    if self.is_immediate_term(draft.payment_term_id):
                        # Pago inmediato
                        draft.payment_term_id = 13
                        payment = self.create_payment(draft, bill['bank_id'])
                        payment.post()
            partner_exists = self.get_partner_or_create_validation(draft.partner_id)

            if partner_exists:
                mensaje3 = 'Algunas facturas tienen un contacto con RFC que ya esxite en el sistema, vaya al menu "Contactos por combinar" para poder combinarlos.'

            invoice_ids.append(draft.id)

        mensaje1 = 'Facturas cargadas: ' + str(len(invoice_ids)) + '\n'
        mensaje1 = mensaje1 + mensaje3
        mensaje2 = mensaje1 + '\nFacturas no cargadas: ' + str(len(invalid_bills))
        invalids = '\n'.join(invalid_bills)
        mensaje2 = mensaje2 + '\n' + invalids
        view = self.env.ref('itlighten_xml_to_invoice.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message'] = mensaje2
        context['invoice_ids'] = invoice_ids
        
        return invoice_ids, mensaje2
        """
        return {
            'name': 'Advertencia',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context
        }
        """
        