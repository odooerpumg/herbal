# -*- coding: utf-8 -*-
{
     'name': "Parent Account",
    'summary': """
        Adds Parent account and ability to open chart of account list view based on the date and moves""",
    'description': """
This module will be very useful for those who are still using v7/v8 because of the no parent account and chart of account heirarchy view in the latest versions
        * Adds parent account in account
        * Adds new type 'view' in account type
        * Adds Chart of account heirachy view
        * Adds credit, debit and balance in account
        * Shows chart of account based on the date and target moves we have selected
    - Need to set the group show chart of account structure to view the chart of account heirarchy.
    
    Contact us for any need of customisation or chart of account migration from v7/v8 - v9/v10
    """,

    'author': 'Steigend IT Solutions, Odoo Community Association (OCA)',
    'website': 'http://www.steigendit.com',
    'category': 'Accounting &amp; Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base'],
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/open_chart.xml',
        'data/account_type_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}