# -*- coding: utf-8 -*-
{
    'name': "ITL Fiscalyear lock date",

    'summary': """
        Este módulo agrega un permiso para mostrar o no el menú de Fechas de bloqueo para años fiscales.""",

    'description': """
        Este módulo agrega un permiso para mostrar o no el menú de Fechas de bloqueo para años fiscales.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
