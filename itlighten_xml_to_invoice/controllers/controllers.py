# -*- coding: utf-8 -*-
# from odoo import http


# class ItlightenXmlToInvoice(http.Controller):
#     @http.route('/itlighten_xml_to_invoice/itlighten_xml_to_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/itlighten_xml_to_invoice/itlighten_xml_to_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('itlighten_xml_to_invoice.listing', {
#             'root': '/itlighten_xml_to_invoice/itlighten_xml_to_invoice',
#             'objects': http.request.env['itlighten_xml_to_invoice.itlighten_xml_to_invoice'].search([]),
#         })

#     @http.route('/itlighten_xml_to_invoice/itlighten_xml_to_invoice/objects/<model("itlighten_xml_to_invoice.itlighten_xml_to_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('itlighten_xml_to_invoice.object', {
#             'object': obj
#         })
