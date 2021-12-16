# -*- coding: utf-8 -*-
{
    'name': "ITL Preselect Warehouse",

    'summary': """
        Este módulo permite preseleccionar el warehouse en la venta 
        de acuerdo a cierta configuración.""",

    'description': """
        Este módulo permite preseleccionar el warehouse en la venta 
        de acuerdo a cierta configuración.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','sale_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/user_warehouse_views.xml',
        'views/sale_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
