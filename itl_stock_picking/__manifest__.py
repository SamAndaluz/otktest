# -*- coding: utf-8 -*-
{
    'name': "ITL Stock picking",

    'summary': """
        Este módulo crea y timbra una factura desde la orden de salida una vez validada.""",

    'description': """
        Este módulo crea y timbra una factura desde la orden de salida una vez validada 
        dependiendo de si el cliente tiene información de Uso de CFDI, Forma de pago y Término de pago.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
