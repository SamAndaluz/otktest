# -*- coding: utf-8 -*-
{
    'name': "itl_eq_email_bcc",

    'summary': """
        Modifications to eq_email_bcc""",

    'description': """
        This module creates modifications to eq_email_bcc module due there are some
        problems transforming the jinja compatible expression returning just the string.
    """,

    'author': "ITLglobal",
    'website': "https://www.itlglobal.tech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'eq_email_bcc'],
}
