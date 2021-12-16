# -*- coding: utf-8 -*-
{
    'name': "ITL l10n_mx_edi Extended",

    'summary': """
        Este módulo sobre escribe la función que calcula los impuestos para diferenciar 
        entre un impuesto normal y un grupo de impuestos.""",

    'description': """
        Este módulo sobre escribe la función que calcula los impuestos para diferenciar 
        entre un impuesto normal y un grupo de impuestos.
    """,

    'author': "ITLighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
