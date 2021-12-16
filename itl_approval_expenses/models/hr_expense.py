import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class HrExpenseCustom(models.Model):
    _inherit = "hr.expense"
    
    # Inherit
    @api.onchange('product_id', 'company_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name or ''
            if not self.attachment_number or (self.attachment_number and not self.unit_amount):
                self.unit_amount = self.product_id.price_compute('standard_price')[self.product_id.id]
            self.product_uom_id = self.product_id.uom_id
            self.tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.company_id)  # taxes only from the same company
            account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account and self.is_editable:
                self.account_id = account
            if self.env.context.get('itl_advance_origin'):
                self.account_id = self.company_id.itl_account_anticipo_id
    
    # Add new filter: check if there are attachments to change status
    def _create_sheet_from_expenses(self):
        sheet = super(HrExpenseCustom, self)._create_sheet_from_expenses()
        
        # Attachments filter
        if any(not expense.advance and expense.attachment_number == 0 for expense in self):
            raise UserError(_("You can not create report without attachment documents."))
            
        return sheet
    
    # Inherit
    def action_move_create(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        move_group_by_sheet = self._get_account_move_by_sheet()

        move_line_values_by_expense = self._get_account_move_line_values()

        move_to_keep_draft = self.env['account.move']

        company_payments = self.env['account.payment']

        for expense in self:
            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id != company_currency

            # get the account move of the related sheet
            move = move_group_by_sheet[expense.sheet_id.id]

            # get move line values
            move_line_values = move_line_values_by_expense.get(expense.id)
            move_line_dst = move_line_values[-1]
            total_amount = move_line_dst['debit'] or -move_line_dst['credit']
            total_amount_currency = move_line_dst['amount_currency']

            # create one more move line, a counterline for the total on payable account
            if expense.payment_mode == 'company_account':
                if not expense.sheet_id.bank_journal_id.default_credit_account_id:
                    raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.sheet_id.bank_journal_id.name))
                journal = expense.sheet_id.bank_journal_id
                # create payment
                payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
                journal_currency = journal.currency_id or journal.company_id.currency_id
                payment = self.env['account.payment'].create({
                    'payment_method_id': payment_methods and payment_methods[0].id or False,
                    'payment_type': 'outbound' if total_amount < 0 else 'inbound',
                    'partner_id': expense.employee_id.address_home_id.commercial_partner_id.id,
                    'partner_type': 'supplier',
                    'journal_id': journal.id,
                    'payment_date': expense.date,
                    'state': 'draft',
                    'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
                    'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
                    'name': expense.name,
                })
                move_line_dst['payment_id'] = payment.id

            # link move lines to move, and move to expense sheet
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            expense.sheet_id.write({'account_move_id': move.id})
            
            if expense.sheet_id.itl_advance_origin:
                move.write({'journal_id': self.company_id.itl_special_expense_journal_id.id})
                #expense.sheet_id.state = 'done'
                
            if expense.payment_mode == 'company_account':
                company_payments |= payment
                if journal.post_at == 'bank_rec':
                    move_to_keep_draft |= move

                expense.sheet_id.paid_expense_sheets()

        company_payments.filtered(lambda x: x.journal_id.post_at == 'pay_val').write({'state':'reconciled'})
        company_payments.filtered(lambda x: x.journal_id.post_at == 'bank_rec').write({'state':'posted'})

        # post the moves
        for move in move_group_by_sheet.values():
            if move in move_to_keep_draft:
                continue
            move.post()
        #raise ValidationError("Testing***")
        return move_group_by_sheet
    
    # Inherit
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_dest_id = self.env['account.account'].browse(account_dst)
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.address_home_id.commercial_partner_id.id

            # source move line
            amount = taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])
            
            if expense.sheet_id.itl_advance_origin:
                credit = move_line_src['credit']
                debit = move_line_src['debit']
                move_line_src['debit'] = credit
                move_line_src['credit'] = debit
                move_line_src['partner_id'] = expense.partner_id.id
                
            move_line_values.append(move_line_src)

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                else:
                    base_amount = None
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                
                if expense.sheet_id.itl_advance_origin:
                    credit = move_line_tax_values['credit']
                    debit = move_line_tax_values['debit']
                    move_line_tax_values['debit'] = credit
                    move_line_tax_values['credit'] = debit
                    move_line_tax_values['partner_id'] = expense.partner_id.id
                    # extra move line
                    move_line_extra = {
                        'name': tax['name'],
                        'quantity': 1,
                        'debit': debit,
                        'credit': credit,
                        'amount_currency': amount_currency if different_currency else 0.0,
                        'account_id': self.company_id.itl_account_iva_pag_id.id,
                        'tax_repartition_line_id': tax['tax_repartition_line_id'],
                        'tag_ids': tax['tag_ids'],
                        'tax_base_amount': base_amount,
                        'expense_id': expense.id,
                        'partner_id': expense.partner_id.id,
                        'currency_id': expense.currency_id.id if different_currency else False,
                        'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                        'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                    }
                    
                    move_line_extra2 = {
                        'name': tax['name'],
                        'quantity': 1,
                        'debit': credit,
                        'credit': debit,
                        'amount_currency': amount_currency if different_currency else 0.0,
                        'account_id': account_src.id,
                        'tax_repartition_line_id': tax['tax_repartition_line_id'],
                        'tag_ids': tax['tag_ids'],
                        'tax_base_amount': base_amount,
                        'expense_id': expense.id,
                        'partner_id': expense.partner_id.id,
                        'currency_id': expense.currency_id.id if different_currency else False,
                        'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                        'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                    }
                    
                    move_line_values.append(move_line_extra)
                    move_line_values.append(move_line_extra2)
                    
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': expense.partner_id.id,
            }
            
            if expense.sheet_id.itl_advance_origin:
                credit = move_line_dst['credit']
                debit = move_line_dst['debit']
                move_line_dst['debit'] = credit
                move_line_dst['credit'] = debit
                
            move_line_values.append(move_line_dst)
            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

class HrExpenseSheetCustom(models.Model):
    _inherit = "hr.expense.sheet"
    
    itl_advance_origin = fields.Boolean(string="Advance origin")
    itl_payment_ids = fields.Many2many('account.payment', string="Payments")
    
    approval_request_id = fields.Many2one('approval.request', string="Approval request", readonly=True, store=True, copy=False)
    approval_status = fields.Selection([
        ('new', 'To Submit'),
        ('pending', 'Submitted'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], related="approval_request_id.request_status")
    
    # Inherit
    @api.model
    def _default_bank_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        acc_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('company_id', '=', default_company_id), ('currency_id.name','=','MXN')], limit=1)
        return self.env['account.journal'].search([('type', 'in', ['cash', 'bank']), ('company_id', '=', default_company_id), ('currency_id.name','=','MXN')], limit=1)
    
    # Inherit
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True, domain="[('type', 'in', ['cash', 'bank']), ('company_id', '=', company_id), ('currency_id.name','=','MXN')]",
        default=_default_bank_journal_id, help="The payment method used when the expense is paid by the company.")
    
    # Inherit
    def action_submit_sheet(self):
        self.send_to_approve()
    
    def send_to_approve(self):
        if not self.env.company.itl_expense_approval_category_id:
            raise ValidationError("Approval category is not configured.")

        approval_obj = self.env['approval.request']
        vals = {
            'name': 'Expense - ' + self.name,
            'request_owner_id': self.env.user.id,
            'category_id': self.env.company.itl_expense_approval_category_id.id,
            'amount': self.total_amount,
            'expense_sheet_id': self.id,
        }
        
        self.state = 'submit'
        if not self.approval_request_id:
            rec = approval_obj.create(vals)
            rec._onchange_category_id()
            rec.action_confirm()
        else:
            rec = self.approval_request_id
            rec.write(vals)
            rec.action_draft()
            rec.action_confirm()

        self.approval_request_id = rec.id

        self.message_post_with_view('itl_approval_expenses.message_approval_expense_created_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)

        rec.message_post_with_view('mail.message_origin_link',
                    values={'self': rec, 'origin': self},
                    subtype_id=self.env.ref('mail.mt_note').id)
        
        for line in self.expense_line_ids:
            line.invoice_related_id.has_expense = True
                
    def action_cancel(self):
        rec = super(HrExpenseSheetCustom, self).action_cancel()
        
        if self.approval_request_id:
            self.approval_request_id.action_cancel()
            self.approval_request_id._get_all_approval_activities().unlink()
            
    def button_refused(self):
        self.state = 'cancel'
        if self.approval_request_id:
            self.approval_request_id._get_all_approval_activities().unlink()
    
    # Inherit
    def approve_expense_sheets(self):
        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve', 'user_id': responsible_id})
        
    # Inherit
    def open_clear_advance(self):
        self.ensure_one()
        action = self.env.ref(
            "hr_expense_advance_clearing." "action_hr_expense_sheet_advance_clearing"
        )
        vals = action.read()[0]
        context1 = vals.get("context", {})
        if context1:
            context1 = safe_eval(context1)
        context1["default_advance_sheet_id"] = self.id
        context1["default_itl_advance_origin"] = True
        vals["context"] = context1
        return vals
    
    # Inherit
    def action_sheet_move_create(self):
        res = super(HrExpenseSheetCustom, self).action_sheet_move_create()
        
        for expense in self.expense_line_ids:
            if expense.invoice_related_id:
                if expense.invoice_related_id.state == 'draft':
                    expense.invoice_related_id.action_post()
                expense.invoice_related_id.invoice_payment_state = 'paid'
                expense.invoice_related_id.amount_residual = 0
                expense.invoice_related_id.expense_id = expense
        
        if self.itl_advance_origin:
            self.write({'state': 'done'})
        
        return res