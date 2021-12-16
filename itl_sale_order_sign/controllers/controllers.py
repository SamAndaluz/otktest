# -*- coding: utf-8 -*-
import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression

import logging
_logger = logging.getLogger(__name__)


class ItlSaleOrderSign(CustomerPortal):

    @http.route('/itl_sale_order_sign/orders/', type='json', auth='user')
    def object(self, **kw):
        sale_order = kw.get('sale_order')
        SaleOrder = request.env['sale.order'].sudo()
        
        domain = [('name','=',sale_order),
                 ('state', 'in', ['sale','done']),
                 ('approval_status','=','approved')]
        
        sale_ids = SaleOrder.search(domain)
        
        valid_sales = request.env['sale.order']
        vals = {}
        results = []
        found_so = False
        for sale in sale_ids:
            found_so = True
            pickings = sale.mapped('picking_ids')
            pickings = pickings.filtered(lambda p: p.state not in ['draft','cancel'] and p.itl_first_review)
            
            internals = []
            outgoings = []
            picking_states = pickings.mapped('state')
            
            all_done = True
            for ps in picking_states:
                if ps != 'done':
                    all_done = False
            if sale.signature:
                return {'results': results, 'found_so': found_so, 'found_so_num': len(sale_ids), 'was_done': True}
            if not pickings:
                results.append({'found_picking': False})
                _logger.info("---<> no picking")
                return {'results': results, 'found_so': found_so, 'found_so_num': len(sale_ids), 'was_done': False}
            for p in pickings:
                if p.picking_type_id.code == 'internal':
                    if p.state == 'done':
                        internals.append(True)
                    else:
                        internals.append(False)
                if p.picking_type_id.code == 'outgoing':
                    if p.state == 'assigned':
                        outgoings.append(True)
                    else:
                        outgoings.append(False)
            
            if all(internals) and all(outgoings):
                vals = {'so_name': sale.name, 'partner_name': sale.partner_id.name, 'sale_type': sale.type_id.name, 'share_url': sale.with_context(only_sign=True)._get_share_url()}
                results.append(vals)
        
        return {'results': results, 'found_so': found_so, 'found_so_num': len(sale_ids)}

    @http.route(['/my/orders_sign/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_sign_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s') % order_sudo.partner_id.name
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            'sale_order': order_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
            'no_breadcrumbs': True
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                                                     (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total, order_sudo.currency_id, order_sudo.partner_id.country_id.id)

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('itl_sale_order_sign.sale_order_sign_template', values)
    
    @http.route(['/my/orders_sign/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_order_sign_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}
        _logger.info("--> portal_order_sign_accept")
        #if not order_sudo.has_to_be_signed():
        #    return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        picking_ids = order_sudo.picking_ids
        last_picking_outgoing = picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing' and x.state == 'assigned').sorted(key=lambda r: r.create_date)
        
        if last_picking_outgoing:
            last_picking_outgoing = last_picking_outgoing[0]
        else:
            raise ValidationError("La orden de venta no está lista.")
            
        inmediate_transfer = request.env['stock.immediate.transfer'].sudo().create({'pick_ids': [(4, last_picking_outgoing.id)]})
        inmediate_transfer.itl_process()
        #if not order_sudo.has_to_be_paid():
        #    order_sudo.action_confirm()
        #    order_sudo._send_order_confirmation_mail()

        #pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([order_sudo.id])[0]

        #_message_post_helper(
        #    'sale.order', order_sudo.id, _('Order signed by %s') % (name,),
        #    attachments=[('%s.pdf' % order_sudo.name, pdf)],
        #    **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        #if order_sudo.has_to_be_paid(True):
        #    query_string += '#allow_payment=yes'
        return {
            'force_refresh': True,
            'redirect_url': False,
        }