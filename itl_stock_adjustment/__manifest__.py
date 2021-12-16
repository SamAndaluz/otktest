# -*- coding: utf-8 -*-
{
    'name': "itl_stock_adjustment",

    'summary': """
        This module is used to create manual inventory adjustments globally.
    """,

    'description': """
        This module is used to create global manual inventory adjustments
        distributed by different managers having functionality as:
        - visualization by warehouse ownership.
        - having a deadline for given report.
        - counting damage products.
        - send email to managers when we need to fill the report.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly.
    'depends': [
        'base',
        'stock',
        'stock_operating_unit',
        'itl_monthly_average_cost',
        'itl_inventory_moving',
        'itl_stock_operating_unit',
        'itl_eq_email_bcc'],

    # always loaded
    'data': [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'data/email_template.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
