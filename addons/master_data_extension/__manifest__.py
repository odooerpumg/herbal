# -*- coding: utf-8 -*-
{
    'name': "Master Data Extension",

    'summary': """
        To import the Master Data""",

    'description': """
        Long description of module's purpose
    """,

    'author': "UMG's ODOO DEVELOPER",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/master_data_views.xml',
        'views/master_menu.xml',
        'views/hr_country.xml',
        'views/hr_region.xml',
        'views/hr_district.xml',
        'views/hr_city.xml',
        'views/hr_township.xml',
        'views/business_type.xml',
        'views/industry_zone.xml',
        'views/building_floor.xml',
        'views/business_unit.xml',
        'views/hr_employee.xml',
        'views/res_users.xml',
        'views/res_company.xml',
        'views/stock_warehouse.xml',
        'views/stock_location.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
