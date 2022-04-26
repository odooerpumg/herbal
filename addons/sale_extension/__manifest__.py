# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Extension',
    'version': '1.1',
    'category': 'Sales/Sales',
    'summary': 'Sales internal machinery',
    'description': """
This module contains all the common features of Sales Management and eCommerce.
    """,
    'depends': ['sale'],
    'data': [
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
