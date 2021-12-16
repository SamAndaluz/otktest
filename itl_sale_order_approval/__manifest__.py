# -*- coding: utf-8 -*-
{
    'name': "ITL Sale order approval",

    'summary': """
        This module add approval functionality to sale order.""",

    'description': """
        This module add approval functionality to sale order.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','itl_sale_order_type'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'security/security_groups.xml',
        'views/sale_order.xml',
        'views/settings.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
