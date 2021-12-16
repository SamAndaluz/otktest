# -*- coding: utf-8 -*-
{
    'name': "ITL Relate invoice with an Expense",

    'summary': """
        This module allows to relate an invoice with an expense.""",

    'description': """
        This module allows to relate an invoice with an expense.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Expenses',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_expense', 'itl_approval_expenses'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
