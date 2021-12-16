# -*- coding: utf-8 -*-
{
    'name': "Account extended Otsuka",

    'summary': """
        This module add some changes to invoice form.""",

    'description': """
        This module add some changes to invoice form.
    """,

    'author': "Itlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
