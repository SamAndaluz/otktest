# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
from odoo.tools.misc import formatLang, format_date, get_lang

class AccountMove(models.Model):
    _inherit = "account.move"
    

    @api.depends('name', 'state')
    def name_get(self):
        result = []
        for move in self:
            if self._context.get('name_groupby'):
                name = '**%s**, %s' % (format_date(self.env, move.date), move._get_move_display_name(show_ref=False))
                if move.ref:
                    name += '     (%s)' % move.ref
                if move.partner_id.name:
                    name += ' - %s' % move.partner_id.name
            else:
                name = move._get_move_display_name(show_ref=True)
            result.append((move.id, name))
        return result
    
    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        draft_name = ''
        folio = False
        if self.state == 'draft':
            draft_name += {
                'out_invoice': _('Draft Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.type]
            if not self.name or self.name == '/':
                draft_name += ' (* %s)' % str(self.id)
            else:
                draft_name += ' ' + self.name
        if self.ref and '-' in self.ref:
            folio = str(self.ref).split('-')
            folio = str(folio[0]).strip()
        elif self.ref:
            folio = self.ref
        if show_ref:
            if folio:
                if self.invoice_date:
                    return (draft_name or self.name) + (' (%s, %s, $%s%s)' % (folio[:50],self.invoice_date.strftime(get_lang(self.env).date_format), self.amount_total, '...' if len(folio) > 50 else ''))
                else:
                    return (draft_name or self.name) + (' (%s, $%s%s)' % (folio[:50], self.amount_total, '...' if len(folio) > 50 else ''))
            else:
                if self.invoice_date:
                    return (draft_name or self.name) + (' (%s, $%s)' % (self.invoice_date.strftime(get_lang(self.env).date_format), self.amount_total))
                else:
                    return (draft_name or self.name) + (' ($%s)' % (self.amount_total))
        else:
            return (draft_name or self.name)