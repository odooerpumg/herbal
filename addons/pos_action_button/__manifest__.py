# -*- coding: utf-8 -*-
{
    'name': 'POS Dashboard',
    'version': '13.0.1.0',
    'summary': 'Dashboard button in POS screen',
    'category': 'Point Of Sales',
    'author': "UMG's ODOO DEVELOPER",
    'maintainer': 'Odoo Beats',
    'company': 'Odoo Beats',
    'website': 'https://www.odoobeats.com',
    'depends': ['base', 'point_of_sale'],
    'qweb': ['static/src/view/action_button.xml'],
    'data': ['views/view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}