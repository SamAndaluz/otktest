# -*- coding: utf-8 -*-
{
    'name': "ITL Payment Without Invoice",

    'summary': """
        Este módulo permite agregar un número de pedimento o número de factura de proveedor 
        en un Payment Resquest para evitar doble pago.""",

    'description': """
        Este módulo permite agregar un número de pedimento o número de factura de proveedor 
        en un Payment Resquest para evitar doble pago.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','itl_approval_vendor_bill','purchase_deposit','itl_inventory_moving'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/approval_request.xml',
        'views/settings.xml',
        'views/templates.xml',
        'views/payment_control_views.xml',
        'views/account_move_views.xml',
        'wizard/payment_request.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
