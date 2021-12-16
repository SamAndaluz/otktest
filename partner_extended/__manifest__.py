# -*- coding: utf-8 -*-
{
    'name': "ITL Partner extended",

    'summary': """
        Este módulo agrega los campos 'Es cliente' y 'Es proveedor' en la ficha del contacto. 
        Además, crea permisos para indicar quien puede crear contactos Clientes o Proveedores.""",

    'description': """
        Este módulo agrega los campos 'Es cliente' y 'Es proveedor' en la ficha del contacto. 
        Además, crea permisos para indicar quien puede crear contactos Clientes o Proveedores.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",
    
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','sale','purchase','account','sale_management'],

    # always loaded
    'data': [
        'security/partner_security.xml',
        'views/res_partner.xml',
        'views/templates.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_move_views.xml',
        #'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
