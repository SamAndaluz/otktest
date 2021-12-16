# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    def force_delete_invoice(self):
        attachment = self.env['ir.attachment']
        for invoice in self:
            _logger.info("-> invoice: " + str(invoice))
            attachment_ids = attachment.search([('res_id','=',invoice.id)])
            _logger.info("-> attachment: " + str(attachment_ids))
            for att in attachment_ids:
                att.datas = False
                att.name = 'test'
                att.unlink()
            #invoice.button_draft()
        self.unlink()
            
        return