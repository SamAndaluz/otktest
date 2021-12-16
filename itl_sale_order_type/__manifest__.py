# -*- coding: utf-8 -*-
{
    'name': "ITL Sale order type",

    'summary': """
        This module extends the sale_order_type module functionality.""",

    'description': """
        This module extends the sale_order_type module functionality.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_order_type','itl_approval_sale'],

    # always loaded
    'data': [
        'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/sale_order_type.xml',
        'views/sale_order.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
