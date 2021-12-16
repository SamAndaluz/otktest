# -*- coding: utf-8 -*-
{
    'name': "ITL Sale Order",

    'summary': """
        Este módulo permite que no se pueda cancelar una orden de venta si tiene almenos una factura posteada.""",

    'description': """
        Este módulo permite que no se pueda cancelar una orden de venta si tiene almenos una factura posteada.
    """,

    'author': "ITlighten",
    'website': "https://www.itlighten.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/sale_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
