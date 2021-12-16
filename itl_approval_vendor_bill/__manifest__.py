# -*- coding: utf-8 -*-
{
    'name': "ITL Approval Vendor Bill",

    'summary': """
        Este módulo permite mandar a aprobación la confirmación de una factura de proveedor desde una PO.""",

    'description': """
        Este módulo permite mandar a aprobación la confirmación de una factura de proveedor desde una PO.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','itl_purchase_and_account_move','itl_approvals_general','itl_approval_purchase'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/account_move_views.xml',
        'views/approval_request_views.xml',
        'views/templates.xml',
        'views/res_config_settings.xml',
        'wizard/payment_request.xml',
        'wizard/send_message_feedback.xml',
        'security/security_groups.xml',
        'data/mail_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
