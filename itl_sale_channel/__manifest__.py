# -*- coding: utf-8 -*-
{
    'name': "ITL Sale Channel",

    'summary': """
        This module adds list of channels with analytic account and pricelist related to customer. For Otsuka.""",

    'description': """
        This module adds list of channels with analytic account and pricelist related to customer. For Otsuka.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_channel_views.xml',
        'views/res_partner.xml',
        #'views/account_move.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
