# -*- coding: utf-8 -*-
{
    'name': "ITL Pricelist Approval",

    'summary': """
        Este módulo agrega una nueva forma de computar el precio de un producto desde lista de precios. Además, agrega funcionalidad para aprobar cambios en las pricelist.""",

    'description': """
        Este módulo agrega una nueva forma de computar el precio de un producto desde lista de precios. Además, agrega funcionalidad para aprobar cambios en las pricelist.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_approvals_general','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
        'data/approval_category_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
