# -*- coding: utf-8 -*-
{
    'name': "Product Approval",

    'summary': """
        This module add new product creation flow.""",

    'description': """
        This module add new product creation flow.
    """,

    'author': "Itlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/settings.xml',
        'views/templates.xml',
        'security/product_approval_security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
