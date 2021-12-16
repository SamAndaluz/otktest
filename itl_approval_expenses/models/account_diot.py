from __future__ import division

from contextlib import contextmanager
import locale
import re
import json
import logging
from unicodedata import normalize
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_compare, translate

_logger = logging.getLogger(__name__)


class MxReportPartnerLedger(models.AbstractModel):
    _inherit = "l10n_mx.account.diot"
    
    
    def _group_by_partner_id(self, options, line_id):
        partners = {}
        results = self._do_query_group_by_account(options, line_id)
        mx_country = self.env.ref('base.mx')
        context = self.env.context
        journal_ids = []
        for company in self.env['res.company'].browse(
                context['company_ids']).filtered('tax_cash_basis_journal_id'):
            journal_ids.append(company.tax_cash_basis_journal_id.id)
            journal_ids.append(company.itl_special_expense_journal_id.id)
            #_logger.info("##### company.tax_cash_basis_journal_id: " + str(company.tax_cash_basis_journal_id.name))
            #_logger.info("#####** company.itl_special_expense_journal_id: " + str(company.itl_special_expense_journal_id.name))
        tax_ids = self.env['account.tax'].with_context(active_test=False).search([
            ('type_tax_use', '=', 'purchase'),
            ('tax_exigibility', '=', 'on_payment')])
        account_tax_ids = tax_ids.mapped('invoice_repartition_line_ids.account_id')
        #_logger.info("##### account_tax_ids: " + str(account_tax_ids.mapped('name')))
        _logger.info("##### journal_ids: " + str(journal_ids))
        base_domain = [
            ('date', '<=', context['date_to']),
            ('company_id', 'in', context['company_ids']),
            ('journal_id', 'in', journal_ids),
            ('account_id', 'not in', account_tax_ids.ids),
            ('tax_ids', 'in', tax_ids.ids),
        ]

        if context['date_from_aml']:
            base_domain.append(('date', '>=', context['date_from_aml']))
        without_vat = []
        without_too = []
        for partner_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('partner_id', '=', partner_id))
            partner = self.env['res.partner'].browse(partner_id)
            partners[partner] = result
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first
                # 80 amls. We will use the 81st to know if there are more than
                # 80 in which case a link to the list view must be displayed.
                partners[partner]['lines'] = self.env[
                    'account.move.line'].search(domain, order='date', limit=81)
            else:
                partners[partner]['lines'] = self.env[
                    'account.move.line'].search(domain, order='date')
            _logger.info("==> partners[partner]['lines']: " + str(partners[partner]['lines'].mapped('id')))
            if partner.country_id == mx_country and not partner.vat and partners[partner]['lines']:
                without_vat.append(partner.name)

            if not partner.l10n_mx_type_of_operation and partners[partner]['lines']:
                without_too.append(partner.name)

        if (without_vat or without_too) and self._context.get('raise'):
            msg = _('The report cannot be generated because of: ')
            msg += (
                _('\n\nThe following partners do not have a '
                  'valid RFC: \n - %s') %
                '\n - '.join(without_vat) if without_vat else '')
            msg += (
                _('\n\nThe following partners do not have a '
                  'type of operation: \n - %s') %
                '\n - '.join(without_too) if without_too else '')
            msg += _(
                '\n\nPlease fill the missing information in the partners and '
                'try again.')

            raise UserError(msg)

        return partners
    
    def _do_query_group_by_account(self, options, line_id):
        select = ',\"account_move_line_account_tax_rel\".account_tax_id, SUM(\"account_move_line\".debit - \"account_move_line\".credit)'  # noqa
        sql = "SELECT \"account_move_line\".partner_id%s FROM %s WHERE %s%s AND \"account_move_line_account_tax_rel\".account_move_line_id = \"account_move_line\".id GROUP BY \"account_move_line\".partner_id, \"account_move_line_account_tax_rel\".account_tax_id"  # noqa
        context = self.env.context
        journal_ids = []
        for company in self.env['res.company'].browse(context[
                'company_ids']).filtered('tax_cash_basis_journal_id'):
            journal_ids.append(company.tax_cash_basis_journal_id.id)
            journal_ids.append(company.itl_special_expense_journal_id.id)
        tax_ids = self.env['account.tax'].with_context(active_test=False).search([
            ('type_tax_use', '=', 'purchase'),
            ('tax_exigibility', '=', 'on_payment')])
        account_tax_ids = tax_ids.mapped('invoice_repartition_line_ids.account_id')
        domain = [
            ('journal_id', 'in', journal_ids),
            ('account_id', 'not in', account_tax_ids.ids),
            ('tax_ids', 'in', tax_ids.ids),
            ('date', '>=', context['date_from']),
            ('move_id.state', '=', 'posted'),
        ]
        tables, where_clause, where_params = self.env[
            'account.move.line']._query_get(domain)
        tables += ',"account_move_line_account_tax_rel"'
        line_clause = line_id and\
            ' AND \"account_move_line\".partner_id = ' + str(line_id) or ''
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        result = {}
        for res in results:
            result.setdefault(res[0], {}).setdefault(res[1], res[2])
        return result