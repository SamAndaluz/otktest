# -*- coding: utf-8 -*-
{
    'name': "ITL Monthly Average Cost",

    'summary': """
        Este módulo genera una póliza contable antes de la recepción de mercancía y se valida
        la recepción hasta que se tengan los costos extra de la importación.""",

    'description': """
        Este módulo genera una póliza contable antes de la recepción de mercancía y se valida
        la recepción hasta que se tengan los costos extra de la importación.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
