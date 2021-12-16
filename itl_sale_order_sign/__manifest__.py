# -*- coding: utf-8 -*-
{
    'name': "ITL Sale Order Sign",

    'summary': """
        Permite buscar una Sale Order, mostrar el detalle de la misma y habilitar la firma del cliente para confirmarla y facturarla.""",

    'description': """
        Este módulo permite que un usuario repartidor pueda buscar una Sale Order desde un nuevo menú para que un cliente pueda firmar de recibido y así se confirme la orden, se haga la salida del inventario y se cree y envíe la factura.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','itl_sale_order_type','itl_inventory_moving'],

    # always loaded
    'data': [
        'security/security_groups.xml',
        'views/views.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        'views/sale_sign_template.xml',
        #'security/ir.model.access.csv',
    ],
    'qweb': [
        "static/src/xml/sale_order_search.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
