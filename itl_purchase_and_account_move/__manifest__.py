# -*- coding: utf-8 -*-
{
    'name': "ITL Purchase Order and Account Move",

    'summary': """
        Este módulo agrega un check box para indicar si ya se recibió el consumible o servicio y habilita el botón de Pagar factura.""",

    'description': """
        Este módulo agrega un check box para indicar si ya se recibió el consumible o servicio y habilita el botón de Pagar factura.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account','purchase_stock','itl_approval_purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/purchase_views.xml',
        #'views/account_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
