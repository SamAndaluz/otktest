# -*- coding: utf-8 -*-
{
    'name': "ITL Inventory Moving",

    'summary': """
        Este módulo agrega funcionalidad para flujo de aprobación de tranferencias de inventario (entradas, salidas, transferencias internas)""",

    'description': """
        Este módulo agrega funcionalidad para flujo de aprobación de tranferencias de inventario (entradas, salidas, transferencias internas)
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','itl_approvals_general','itl_approval_sale','mail'],

    # always loaded
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/logistic_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/stock_move_line_view.xml',
        'views/stock_scrap_view.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
        'views/stock_move_views.xml',
        'views/approval_request_views.xml',
        'views/sale_order_type.xml',
        'views/prepare_picking_views.xml',
        'views/stock_warehouse_views.xml',
        'wizard/send_message_feedback.xml',
        'data/approval_category_data.xml',
        'data/mail_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
