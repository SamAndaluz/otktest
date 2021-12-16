# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountReconciliationCustom(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    
    @api.model
    def _get_bank_statement_line_partners(self, st_lines):
        params = []

        # Add the res.partner.ban's IR rules. In case partners are not shared between companies,
        # identical bank accounts may exist in a company we don't have access to.
        ir_rules_query = self.env['res.partner.bank']._where_calc([])
        self.env['res.partner.bank']._apply_ir_rules(ir_rules_query, 'read')
        from_clause, where_clause, where_clause_params = ir_rules_query.get_sql()
        if where_clause:
            where_bank = ('AND %s' % where_clause).replace('res_partner_bank', 'bank')
            params += where_clause_params
        else:
            where_bank = ''

        # Add the res.partner's IR rules. In case partners are not shared between companies,
        # identical partners may exist in a company we don't have access to.
        ir_rules_query = self.env['res.partner']._where_calc([])
        self.env['res.partner']._apply_ir_rules(ir_rules_query, 'read')
        from_clause, where_clause, where_clause_params = ir_rules_query.get_sql()
        if where_clause:
            where_partner = ('AND %s' % where_clause).replace('res_partner', 'p3')
            params += where_clause_params
        else:
            where_partner = ''

        query = '''
            SELECT
                st_line.id                          AS id,
                COALESCE(p1.id,p2.id,p3.id)         AS partner_id
            FROM account_bank_statement_line st_line
        '''
        query += "LEFT JOIN res_partner_bank bank ON bank.id = st_line.bank_account_id OR bank.sanitized_acc_number ILIKE regexp_replace(st_line.account_number, '\W+', '', 'g') %s\n" % (where_bank)
        query += 'LEFT JOIN res_partner p1 ON st_line.partner_id=p1.id \n'
        query += 'LEFT JOIN res_partner p2 ON bank.partner_id=p2.id AND st_line.partner_id=p2.id \n'
        # By definition the commercial partner_id doesn't have a parent_id set
        query += 'LEFT JOIN res_partner p3 ON p3.name ILIKE st_line.partner_name %s AND p3.parent_id is NULL \n' % (where_partner)
        query += 'WHERE st_line.id IN %s'

        params += [tuple(st_lines.ids)]

        self._cr.execute(query, params)

        result = {}
        for res in self._cr.dictfetchall():
            result[res['id']] = res['partner_id']
        return result
