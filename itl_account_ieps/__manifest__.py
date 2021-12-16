# -*- coding: utf-8 -*-
{
    'name': "ITL Account IEPS",

    'summary': """
        Este módulo hace algunos ajustes adicionales al ajuste del IEPS al crear una factura 
        desde una orden de venta.""",

    'description': """
        Este módulo hace algunos ajustes adicionales al ajuste del IEPS al crear una factura 
        desde una orden de venta.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/sale_views.xml',
        'views/templates.xml',
        'views/res_config_settings_views.xml',
        'report/report_invoice.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
