# -*- encoding: utf-8 -*-

{
    'name': 'Master Data Import',
    'category': 'Master',
    'version': '0.1',
    'author': 'Infinite Business Solution Co.,Ltd',
    'website': '',
    'summary': 'Master Data Import',
    'data': [
        'security/ir.model.access.csv',
        'views/master_import_view.xml',
        'views/payment_method_import.xml'
    ],
    'application': 'True',
    'depends': ['base', 'base_import'],
    'description':  """
Module of Master Data Excel Import
==================================

Master data import module that covers:
--------------------------------------
    * Education Master Data
Can use all versions of excel file such as .xls and .xlsx.
"""
}