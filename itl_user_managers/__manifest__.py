# -*- coding: utf-8 -*-
{
    'name': "itl_user_managers",

    'summary': """
        ITL user managers""",

    'description': """
        ITL user managers
    """,

    'author': "ITLighten",
    'website': "http://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/sale_order_groups.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
