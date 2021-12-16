# -*- coding: utf-8 -*-
{
    'name': "ITL Approval discount and price unit in Sale Order",

    'summary': """
        Este módulo agrega la funcionalidad para aprobar la solicitud de cambio de precio unitario o descuento 
        en las líneas de una Sale Order.""",

    'description': """
        Este módulo agrega la funcionalidad para aprobar la solicitud de cambio de precio unitario o descuento 
        en las líneas de una Sale Order.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','itl_approvals_general'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_views.xml',
        'views/approval_request_views.xml',
        'views/res_config_settings_views.xml',
        'views/templates.xml',
        'wizard/send_message_feedback.xml',
        'data/approval_category_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
