# -*- coding: utf-8 -*-
{
    'name': "ITL Approval Contact",

    'summary': """
        Este módulo usa el módulo Approvals y le agrega lógica para aprobar contactos.""",

    'description': """
        Este módulo usa el módulo Approvals y le agrega lógica para aprobar contactos.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_approvals_general'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
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
