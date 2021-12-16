# -*- coding: utf-8 -*-
{
    'name': "itl_status_control_screen",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','sale','hr_expense','itl_approval_purchase','itl_approval_vendor_bill'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/sale_views.xml',
        'views/expense_sheet_views.xml',
        'views/menu_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True
}
