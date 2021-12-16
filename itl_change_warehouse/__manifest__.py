# -*- coding: utf-8 -*-
{
    'name': "ITL Change Warehouse",

    'summary': """
        Este módulo permite cambiar de almacén en una orden de venta ya confirmada.""",

    'description': """
        Este módulo permite cambiar de almacén en una orden de venta ya confirmada.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','itl_inventory_moving'],

    # always loaded
    'data': [
        'security/security_groups.xml',
        #'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/change_warehouse_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
