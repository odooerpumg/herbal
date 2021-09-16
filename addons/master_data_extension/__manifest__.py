# -*- coding: utf-8 -*-
{
    'name': "Master Data Extension",

    'summary': """
        To import the Master Data""",

    'description': """
        Long description of module's purpose
    """,

    'author': "M2h",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

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
        'views/business_unit.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
