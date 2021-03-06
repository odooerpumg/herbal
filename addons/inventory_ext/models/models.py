# -*- coding: utf-8 -*-
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


class NrcNo(models.Model):
    _name = 'nrc.no'

    name = fields.Char('Name')

class NrcDescription(models.Model):
    _name = 'nrc.description'
    name = fields.Char('Name')
    nrc_no_id = fields.Many2one('nrc.no',string='NRC No')

class NrcType(models.Model):
    _name = 'nrc.type'
    name = fields.Char('Name')
    description = fields.Text('Description')

class ResPartner(models.Model):
    """Partner with birth date in date format."""

    _inherit = "res.partner"

    birthdate_date = fields.Date("Birthdate")
    age = fields.Integer(string="Age", readonly=True, compute="_compute_age")    

    # GENDER
    gender  = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender',default='male')
    # REFEREE
    referee_name = fields.Char(string='Referee Name')
    referee_number = fields.Char(string='Referee Number')

    # SECOND CONTACT
    sec_contact_name = fields.Char(string='Second Contact Name')
    sec_contact_number = fields.Char(string='Second Contact Nunmber')

    #CUSTOMER TYPE(UMGian/UMGina Family Member)
    customer_type = fields.Selection([('umgian', 'UMGian'),('umgian_family_member', "UMGian's Family Member")], string='Customer Type')

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

    # NRC
    nrc_no = fields.Many2one('nrc.no',string="NRC No")
    nrc_desc = fields.Many2one('nrc.description',string="NRC Description", domain="[('nrc_no_id','=',nrc_no)]")
    nrc_type = fields.Many2one('nrc.type',string="NRC Type")
    nrc_number = fields.Char('NRC Number')
    
    nrc_string = fields.Char('NRC', compute="_compute_nrc_string")    

    @api.depends("nrc_no", "nrc_desc", "nrc_type", "nrc_number")
    def _compute_nrc_string(self):
        for record in self:
            if record.nrc_no and record.nrc_desc and record.nrc_type and record.nrc_number:
                record.nrc_string = str(record.nrc_no.name) + '/' + str(record.nrc_desc.name) + '(' + str(record.nrc_type.name) + ')' + str(record.nrc_number)
            else:
                record.nrc_string = None

    # EMPLOYEE ID
    umgian_employee_id = fields.Char('Employee ID')

    # BU/BR
    business_unit_id = fields.Many2one('business.unit', string='Business Unit')
    branch_id = fields.Many2one('business.branch',string='Branch')
    
    # BU address
    bu_township_id = fields.Many2one('hr.township', string='BU Township')
    bu_city_id = fields.Many2one('hr.city', string='BU City')
    bu_division_id = fields.Many2one('hr.region', string='BU Division')
    bu_country_id = fields.Many2one('hr.country', string='BU Country')

    @api.onchange('business_unit_id')
    def onchange_business_unit_id(self):
        if self.business_unit_id:
            self.bu_township_id = self.business_unit_id.township_id.id
            self.bu_city_id = self.business_unit_id.city_id.id
            self.bu_division_id = self.business_unit_id.division_id.id
            self.bu_country_id = self.business_unit_id.country_id.id
            
class StockValuationLayerInh(models.Model):
    _inherit = 'stock.valuation.layer'

    location = fields.Char("Current BU/BR/Div",related="stock_move_id.location_dest_id.name")


    