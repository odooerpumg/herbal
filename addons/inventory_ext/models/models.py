# -*- coding: utf-8 -*-

from typing import Text
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

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


class ResPartner(models.Model):
    """Partner with birth date in date format."""

    _inherit = "res.partner"

    birthdate_date = fields.Date("Birthdate")
    age = fields.Integer(string="Age", readonly=True, compute="_compute_age")    

    # REFEREE
    referee_name = fields.Char(string='Referee Name')
    referee_number = fields.Char(string='Referee Number')

    # SECOND CONTACT
    sec_contact_name = fields.Char(string='Second Contact Name')
    sec_contact_number = fields.Char(string='Second Contact Nunmber')

    #CUSTOMER TYPE(UMGian/UMGina Family Member)
    customer_type = fields.Selection([('umgian', 'UMGian'),('umgian_family_member', 'UMGina Family Member')], string='Customer Type')

    # TEXT
    medical_history = fields.Text(string='Medical History')
    remark = fields.Text(string='Remark')

    @api.depends("birthdate_date")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthdate_date:
                age = relativedelta(fields.Date.today(), record.birthdate_date).years
            record.age = age 
