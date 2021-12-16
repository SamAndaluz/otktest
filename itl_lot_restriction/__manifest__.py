# -*- coding: utf-8 -*-
{
    'name': "ITL Lot Restriction",

    'summary': """
        Este módulo permite seleccionar un lote que no tiene disponibilidad.""",

    'description': """
        Este módulo permite seleccionar un lote que no tiene disponibilidad.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','itl_inventory_moving'],

    # always loaded
    'data': [
        'security/security_groups.xml',
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
