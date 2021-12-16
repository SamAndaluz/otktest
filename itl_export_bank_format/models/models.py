 # -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging, base64, unidecode, zipfile, io
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

class itl_customer_form(models.Model):
    _inherit = 'res.partner'
    
    itl_requiresNotification = fields.Boolean(string="Requires Notification (Mizuho)")
    itl_template_generated = fields.Boolean(string="Mizuho Template Generated")
    
class ResBank(models.Model):
    _inherit = 'res.bank'
    
    itl_banxico_legal_name = fields.Char(string="Banxico Legal Name", copy=False)
    itl_banxico_code = fields.Char(string="Baxico Code", copy=False)

class itl_export_bank_format(models.Model):
    _inherit = 'account.move'
    
    itl_alreadyPrinted = fields.Boolean(string="Upload file", track_visibility='onchange')
    #itl_requiresNotification = fields.Boolean(string="Requires notification")
    #itl_relatedBank = fields.Many2one('res.partner.bank', string="Beneficiary bank")

    def itl_printTemplate(self, my_list = []):
        missingFieldsArrItems = []
        fullStrMXN = ""
        fullStrUSD = ""
        
        for item in my_list:
            missingFieldsArr = []
            if item.partner_id.itl_template_generated:
                continue
            fieldsMissing = False
            # 0 = MXN, 1 = USD
            isMXN = True
            myStr = ""

            #1 Template Name - MANDATORY
            if(item.partner_id.name is not False):
                template_name = str(unidecode.unidecode(item.partner_id.name)).replace(',', '.')
                if len(template_name) > 48:
                    template_name = template_name[:48]
                myStr += template_name + ","
            else:
                fieldsMissing = True
                missingFieldsArr.append("Template Name")
            _logger.info("--## myStr: " + str(myStr))
            
            #2 Debit Account Number - MANDATORY
            #3 Debit Account Currency - MANDATORY
                #Otsuka account numbers
            mxn_account_number = "H10-752-204321"
            usd_account_number = "F10-752-404337"
            template_name = ""
            if(str(item.currency_id.name) == "MXN"):
                myStr += mxn_account_number + ","
                myStr += "MXN,,,,,,,,,,,,,,,,,,,,,,,,,,,"
            elif(str(item.currency_id.name) == "USD"):
                myStr += usd_account_number + ","
                myStr += "USD,,,,,,,,,,,,,,,,,,,,,,,,,,,"
                isMXN = False
            
            #4 Beneficiary Clave Number - MANDATORY
            if len(item.partner_id.bank_ids) > 0:
                myStr += str(item.partner_id.bank_ids[0].l10n_mx_edi_clabe).replace(',', '.') + ",,"
            else:
                fieldsMissing = True
                missingFieldsArr.append("Beneficiary Clave Number")

            #5 Beneficiary Country Name - MANDATORY
            if(item.partner_id.country_id.name is not False):
                accented_string = str(item.partner_id.country_id.name)
                unaccented_string = unidecode.unidecode(accented_string)
                myStr += str(unaccented_string).replace(',', '.') + ","
            else:
                fieldsMissing = True
                missingFieldsArr.append("Beneficiary Country Name")

            #6 Beneficiary Name (Up to 40 Characters) - MANDATORY
            if(item.partner_id.name is not False):
                beneficiary_name = str(item.partner_id.name).replace(',', '.')
                if len(beneficiary_name) > 35:
                    beneficiary_name = beneficiary_name[:35]
                beneficiary_name = unidecode.unidecode(beneficiary_name)
                myStr += beneficiary_name + ","
            else:
                fieldsMissing = True
                missingFieldsArr.append("Beneficiary name")

			#7 Beneficiary Addresss 1 (Up to 35 Characters)
            street = ""
            snumber = ""
            colony = ""
            city = ""
            state = ""
            zip_code = ""
            country = ""
            if(item.partner_id.street_name != False):
                street = str(item.partner_id.street_name).replace(',', '.') + " "
            if(item.partner_id.street_number != False):
                snumber = str(item.partner_id.street_number).replace(',', '.') + " "
            if(item.partner_id.l10n_mx_edi_colony != False):
                colony = str(item.partner_id.l10n_mx_edi_colony).replace(',', '.') + " "
            if(item.partner_id.city_id.name != False):
                city = str(item.partner_id.city_id.name).replace(',', '.') + " "
            if(item.partner_id.state_id.name != False):
                state = str(item.partner_id.state_id.name).replace(',', '.') + " "
            if(item.partner_id.zip != False):
                zip_code = str(item.partner_id.zip).replace(',', '.') + " "
            if(item.partner_id.country_id.name != False):
                country = unaccented_string.replace(',', '.') + " "

            #full_address = street + snumber + colony + city + state + zip_code + country
            address_1 = street + snumber + colony
            address_2 = city + state + zip_code + country
            address_1 = unidecode.unidecode(address_1)
            address_2 = unidecode.unidecode(address_2)
            
            if len(address_1) > 35:
                address_1 = address_1[:35]
            if len(address_2) > 35:
                address_2 = address_2[:35]
                
            myStr += address_1 + ","
            
            #8 Beneficiary Address 2 (Up to 35 Characters)
            myStr += address_2 + ",,,,"
            
            #9 Beneficiary RFC Number
            if(item.partner_id.vat is not False):
                myStr += str(item.partner_id.vat).replace(',', '.') + ",,,,,,,,,"
            else:
                missingFieldsArr.append("Beneficiary RFC Number")
                fieldsMissing = True

            #10 Beneficiary Bank Name (Please refer separate Banxico List)
            if len(item.partner_id.bank_ids) > 0:
                myStr += str(item.partner_id.bank_ids[0].bank_id.name).replace(',', '.') + "," + str(item.partner_id.bank_ids[0].bank_id.itl_banxico_legal_name).replace(',', '.') + "," + str(item.partner_id.bank_ids[0].bank_id.itl_banxico_code) + ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
            else:
                missingFieldsArr.append("Beneficiary Bank Name")
                fieldsMissing = True
            #
            #if len(item.partner_id.bank_ids) > 0:
            #    myStr += str(item.partner_id.bank_ids[0].bank_id.l10n_mx_edi_code).replace(',', '.') + ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
            #else:
            #    missingFieldsArr.append("Beneficiary Bank ABM Code")
            #    fieldsMissing = True

            #11 e-Mail Notification (0: Not Required, 1: Required)
            if(item.partner_id.itl_requiresNotification):
                myStr += "1"
            else:
                myStr += "0"
            myStr += ","

            #12 e-Mail Notification e-mail address (If choose 11 as "1" Required)
            if (item.partner_id.itl_requiresNotification):
                if(item.partner_id.email is not False):
                    myStr += str(item.partner_id.email).replace(',', '.')
                else:
                    missingFieldsArr.append("Beneficiary email")
                    fieldsMissing = True
                

            if(fieldsMissing):
                _logger.info(myStr)
                myStr = ""
                missingFieldsArrItems.append([item, missingFieldsArr])
            elif(isMXN):
                fullStrMXN += myStr + "\n"
            else:
                fullStrUSD += myStr + "\n"
#                 TODO Turn on when ready
#                 item.partner_id.itl_is_registered = True   
            item.partner_id.itl_template_generated = True

        _logger.info("***> missingFieldsArrItems: " + str(missingFieldsArrItems))
        if len(missingFieldsArrItems) > 0:
            error_msg = "The templates for the next item could not be generated because they are missing fields:\n"
            for item2 in missingFieldsArrItems:
                error_msg += "- Item invoice " + str(item2[0].name) + ": " + ", ".join(item2[1]) + "\n"
            raise Warning(error_msg)
            
        template_strings = []
        template_strings.append(fullStrMXN)
        template_strings.append(fullStrUSD)

        return template_strings


    def itl_printPaymentFile(self):
        fullStrUSD = ""
        fullStrMXN = ""
        
        notPostedArr = []
        missingFieldsArr = []
        alreadyPrintedArr = []
        toRegisterArr = []
        wrongCurrencyArr = []
        
        bill_ids = self.filtered(lambda i: i.type == 'in_invoice')
        
        for item in bill_ids:
            #TODO if item not approved -> cant export
#             this = self.env['sale.order']
#             recSale = this.search([('state', '=', 'done')])
#             for x in recSale:
#                 x.write({'state': 'draft'})
            missingFields = []
            #if(item.partner_id.itl_is_registered == False):
            toRegisterArr.append(item)
            
            if(item.state not in [('posted')] or not item.approval_vendor_bill_status == 'approved' or item.invoice_payment_state == 'paid'):
                notPostedArr.append(item)
                
            elif(not item.itl_alreadyPrinted):
            #elif(not False):
                isMXN = True
                myStr = ""
                fieldsMissing = False
                #1 Branch Code - MANDATORY
                branch_code = "96001000"
                myStr += branch_code + ","
                
                #2 Payment Method - MANDATORY
                template_name = ""
                if(str(item.currency_id.name) == "MXN"):
                    myStr += "020 Domestic Mexican Peso Payment - CLABE,"
                elif(str(item.currency_id.name) == "USD"):
                    myStr += "050 Domestic US Dollar Payment - CLABED,"
                    isMXN = False
                else:
                    wrongCurrencyArr.append(item)
                
                #3 Template Name - MANDATORY
                if(item.partner_id.name is not False):
                    template_name = str(unidecode.unidecode(item.partner_id.name)).replace(',', '.')
                    if len(template_name) > 48:
                        template_name = template_name[:48]
                    myStr += template_name + ","
                else:
                    fieldsMissing = True
                    missingFieldsArr.append("Template Name")
                    
                #4 Debit Account Number - MANDATORY
                #5 Remittance Currency - MANDATORY
                mxn_account_number = "H10-752-204321"
                usd_account_number = "F10-752-404337"
                
                if(str(item.currency_id.name) == "MXN"):
                    myStr += mxn_account_number + ","
                    myStr += "MXN,"
                else:
                    myStr += usd_account_number + ","
                    myStr += "USD,"
                
                #6 Remittance Amount - MANDATORY
                myStr += str(item.amount_residual).replace(',', '.') + ","

                #7 Value Date - MANDATORY
                dayStr = str('{:02d}'.format(fields.Date.today().day))
                monthStr = str('{:02d}'.format(fields.Date.today().month))
                yearStr = str('{:04d}'.format(fields.Date.today().year))
                myStr += yearStr + monthStr + dayStr + ",,,,,,,,,,,,,,,,,,,,,,,,,"
                
                #8 Beneficiary Clave Number
                #if len(item.partner_id.bank_ids) > 0:
                #    myStr += str(item.partner_id.bank_ids[0].l10n_mx_edi_clabe).replace(',', '.') + ",,"
                #else:
                myStr += "" + ",,"
                #9 Beneficiary Country Name
                unaccented_string = ""
                #if(item.partner_id.country_id.name == False):
                #    unaccented_string = ""
                #else:
                #    accented_string = str(item.partner_id.country_id.name)
                #    unaccented_string = unidecode.unidecode(accented_string)
                myStr += str(unaccented_string).replace(',', '.') + ","

                #10 Beneficiary Name (Up to 40 Characters)
                #if(item.partner_id.name == False):
                myStr += "" + ","
                #else:
                #    beneficiary_name = str(item.partner_id.name).replace(',', '.')
                #    if len(beneficiary_name) > 35:
                #        beneficiary_name = beneficiary_name[:35]
                #    myStr += beneficiary_name + ","

                #11 Beneficiary Addresss 1 (Up to 35 Characters)
                street = ""
                snumber = ""
                colony = ""
                city = ""
                state = ""
                zip_code = ""
                country = ""
                if(item.partner_id.street_name != False):
                    street = str(item.partner_id.street_name).replace(',', '.') + " "
                if(item.partner_id.street_number != False):
                    snumber = str(item.partner_id.street_number).replace(',', '.') + " "
                if(item.partner_id.l10n_mx_edi_colony != False):
                    colony = str(item.partner_id.l10n_mx_edi_colony).replace(',', '.') + " "
                if(item.partner_id.city_id.name != False):
                    city = str(item.partner_id.city_id.name).replace(',', '.') + " "
                if(item.partner_id.state_id.name != False):
                    state = str(item.partner_id.state_id.name).replace(',', '.') + " "
                if(item.partner_id.zip != False):
                    zip_code = str(item.partner_id.zip).replace(',', '.') + " "
                if(item.partner_id.country_id.name != False):
                    country = unaccented_string.replace(',', '.') + " "
                #full_address = street + snumber + colony + city + state + zip_code + country
                address_1 = street + snumber + colony
                address_2 = city + state + zip_code + country
                address_1 = unidecode.unidecode(address_1)
                address_2 = unidecode.unidecode(address_2)
                #if(full_address == ""):
                #    myStr += "Empty,"
                #else:
                #    myStr += full_address + ","
                #if len(address_1) > 35:
                #    address_1 = address_1[:35]
                #if len(address_2) > 35:
                #    address_2 = address_2[:35]
                #myStr += address_1 + ","
                myStr += ","
                #12 Beneficiary Address 2 (Up to 35 Characters)
                #myStr += address_2 + ",,,,"
                myStr += ",,,,"

                #13 Beneficiary RFC Number
                #if(item.partner_id.vat == False):
                myStr += "" + ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
                #else:
                #    myStr += str(item.partner_id.vat).replace(',', '.') + ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"

                #14 Bank Charges (SPED and SPID always use OUR type) - MANDATORY
                share = "1"
                our = "2"
                beneficiary = "3"
                myStr += our + ",,"
                
                #15 e-Mail Notification (0: Not Required, 1: Required)
                #if(item.partner_id.itl_requiresNotification):
                #    myStr += "1"
                #else:
                myStr += "0"
                myStr += ","

                #16 e-Mail Notification e-mail address (If choose 11 as "1" Required)
                #if(item.partner_id.itl_requiresNotification):
                #    if(item.partner_id.email == False):
                myStr += ""
                #    else:
                #        myStr += str(item.partner_id.email).replace(',', '.')
                myStr += ",,,,,,,,,,,,,,"
                    
                #17 Numeric Reference Number (Up to 7 digits)
                if(item.ref == False):
                    #fieldsMissing = True
                    #missingFields.append("Reference")
                    num_ref = str(item.name).split('/')[-1]
                    
                else:
                    num_ref = str(item.ref.split(' ', 1)[0])
                    num_ref = num_ref.split('-', 1)[0]
                    if num_ref == "":
                        num_ref = str(item.name).split('/')[-1]
                if len(num_ref) > 7:
                    num_ref = num_ref[:7]
                num_ref = num_ref[:7]
                myStr += num_ref + ","
                #18 Payment Concept
                if item.invoice_origin:
                    myStr += str(item.invoice_origin).replace(',', '-') + ""
                else:
                    myStr += str(item.name).replace('/', '-') + ""

                if(fieldsMissing):
                    myStr = ""
                    missingFieldsArr.append((item, missingFields))
                elif(isMXN):
                    fullStrMXN += myStr + "\n"
#                     TODO turn on when ready
                     #item.itl_alreadyPrinted = True
                else:
                    fullStrUSD += myStr + "\n"
#                     TODO turn on when ready
                item.itl_alreadyPrinted = True
            else:
                alreadyPrintedArr.append(item)

        warning_msg = ""
        
        if(len(notPostedArr) > 0):
            warning_msg += "The next items are not posted yet or are paid or its payment request is not approved:\n"
            for item in notPostedArr:
                warning_msg += "- The invoice from " + str(item.partner_id.name) + " on " + str(item.date) + "\n"
            raise Warning(warning_msg)
        
        #if(len(alreadyPrintedArr) > 0):
        #    warning_msg += "The next items have already been exported:\n"
        #    for item in alreadyPrintedArr:
        #        warning_msg += "- Invoice " + str(item.name) + "\n"
        #    raise Warning(warning_msg)

        if(len(missingFieldsArr) > 0):
            warning_msg += "The next items are missing mandatory fields:\n"
            for item in missingFieldsArr:
                warning_msg += "- Item invoice " + str(item[0].name) + ": " + ", ".join(item[1]) + "\n"
            raise Warning(warning_msg)
        
        if(len(wrongCurrencyArr) > 0):
            warning_msg += "The next items are not in MXN or USD:\n"
            for item in wrongCurrencyArr:
                warning_msg += "- Invoice " + str(item.name) + "\n"
            raise Warning(warning_msg)
        
        template_strings = self.itl_printTemplate(toRegisterArr)

        zip_stream = io.BytesIO()
        has_data = False
        with zipfile.ZipFile(zip_stream, 'w') as myzip:
            if(len(template_strings[0]) > 0):
                has_data = True
                myzip.writestr("TemplateFilesSPEI.csv", unidecode.unidecode(template_strings[0]))
            if(len(template_strings[1]) > 0):
                has_data = True
                myzip.writestr("TemplateFilesSPID.csv", unidecode.unidecode(template_strings[1]))
            if(len(fullStrMXN) > 0):
                has_data = True
                myzip.writestr("PaymentFilesSPEI.csv", fullStrMXN)
            if(len(fullStrUSD) > 0):
                has_data = True
                myzip.writestr("PaymentFilesSPID.csv", fullStrUSD)
            myzip.close()
        
        if has_data:
            values = {
                'name': 'reports.zip',
                'type': 'binary',
                'mimetype': 'application/zip',
                'public': False,
                'db_datas': base64.b64encode(zip_stream.getvalue())
            }

            attachment = self.env['ir.attachment'].create(values)

            return {
                'type': 'ir.actions.act_url',
    #             'url': '/web/content/%s?download=true' % (attachment_id.id),
                'url': '/web/content/' + str(attachment.id) + '?download=True',
                'target': 'new',
                'nodestroy': False,
            }
        else:
            raise Warning("Nothing to process.")

    
# class MessageWizard(model.TransientModel):
#     _name = 'message.wizard'

#     message = fields.Text('Message', required=True)

#     @api.multi
#     def action_ok(self):
#         """ close wizard"""
#         return {'type': 'ir.actions.act_window_close'}

