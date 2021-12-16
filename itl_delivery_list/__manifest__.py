# -*- coding: utf-8 -*-
{
    'name': "ITL Delivery List Report",

    'summary': """
        Este módulo permite crear un reporte de las órdenes de entrega 
        con un formato proporcionado por el equio de Otsuka.""",

    'description': """
        Este módulo permite crear un reporte de las órdenes de entrega 
        con un formato proporcionado por el equio de Otsuka.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_inventory_moving'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/delivery_list_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
