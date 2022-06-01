# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Extension',
    'version': '1.1',
    'category': 'Purchase Order',
    'summary': 'Purchase internal machinery',
    'description': """
This module contains all the common features of Purchase Management and eCommerce.
    """,
    'depends': ['purchase'],
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
