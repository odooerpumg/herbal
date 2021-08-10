# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # umgian_price: price, user defined
    umgian_price = fields.Float(
        'UMGian Price', default=1.0,
        digits='Product Price',
        help="Price at which the product is sold to UMGian.")

    # umgian_family_price: price, user defined
    umgian_family_price = fields.Float(
        "Family Member Price", default=1.0,
        digits='Family Member Price',
        help="Price at which the product is sold to Family of UMGian.") 
    
    @api.onchange('list_price')
    def _onchange_list_price(self):
        self.umgian_price = self.list_price if self.list_price and self.umgian_price == 1.0 else self.umgian_price
        self.umgian_family_price = self.list_price if self.list_price and self.umgian_family_price == 1.0 else self.umgian_family_price