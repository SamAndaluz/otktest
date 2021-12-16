# -*- coding: utf-8 -*-
{
    'name': "ITL Invoice Approval",

    'summary': """
        This module allows to send invoice to approve if it doesn't have a purchase order.""",

    'description': """
        This module allows to send invoice to approve if it doesn't have a purchase order.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','itl_approval_vendor_bill'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/settings.xml',
        'views/templates.xml',
        'security/account_security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
