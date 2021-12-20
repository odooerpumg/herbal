# -*- coding: utf-8 -*-
{
    'name': 'POS Dashboard',
    'version': '13.0.1.0',
    'summary': 'Dashboard button in POS screen',
    'category': 'Point Of Sales',
    'author': "UMG's ODOO DEVELOPER",
    'maintainer': '',
    'company': '',
    'website': '',
    'depends': ['base', 'point_of_sale', 'inventory_ext'],
    'qweb': [
        'static/src/view/action_button.xml',
        'static/src/view/client_screen.xml',
        # 'static/src/view/numpad_widget.xml',
        'static/src/view/order_receipt.xml',
    ],
    'data': [
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}