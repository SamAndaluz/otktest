# -*- coding: utf-8 -*-
{
    'name': "ITL Relate invoice with Purchase Order",

    'summary': """
        This module allows to relate an invoice with a purchase order.""",

    'description': """
        This module allows to relate an invoice with a purchase order.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account','itl_approval_vendor_bill'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/account_move_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
