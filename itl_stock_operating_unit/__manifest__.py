# -*- coding: utf-8 -*-
{
    'name': "ITL Inventory Report with Operating Units",

    'summary': """
        Este módulo permite filtrar las ubicaciones en el reporte de invetario 
        por aquellas a las que el usuario tiene acceso.""",

    'description': """
        Este módulo permite filtrar las ubicaciones en el reporte de invetario 
        por aquellas a las que el usuario tiene acceso.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock_operating_unit'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
