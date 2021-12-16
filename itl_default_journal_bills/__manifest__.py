# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'ITL Default Journal for Vendor Bill',
    'category': 'Accounting & Finance',
    'summary': 'Automatically select the proper journal for expenses and vendor bills.',
    'website': 'https://www.itlighten.com',
    'license': 'AGPL-3',
    'version': '13.0.1.0.0',
    'description': '''
        This module selects automatically the proper journal for vendor bills.
        ''',
    'author': 'ITLighten',
    'depends': [
        'account'
    ],
    'data': [
        'views/account_journal.xml',
    ],
    'installable': True,
    'application': False,
}
