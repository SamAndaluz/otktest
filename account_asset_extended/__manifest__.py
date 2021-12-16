# -*- coding: utf-8 -*-
{
    'name': "assests_extended",

    'summary': """
        This module extend assets functionality""",

    'description': """
        This module extend assets functionality
    """,

    'author': "A. Márquez",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_asset.xml',
        'views/hr_employee.xml',
        'views/templates.xml',
        'views/res_partner.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
