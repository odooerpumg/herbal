# -*- coding: utf-8 -*-
{
    'name': "Inventory Extension",

    'summary': "To modify  product, stock and logistics activities",

    'description': "",
    'author': "UMG's ODOO DEVELOPER",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'master_data_extension','stock_account'],

    # always loaded
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/nrc_views.xml',
        'views/bu_br_views.xml',
        'views/stock_valuation_layer_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
