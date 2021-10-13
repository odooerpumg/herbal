# -*- coding: utf-8 -*-
from odoo import models, fields, api

# DIVISION
class HrRegion(models.Model):
	_name = 'hr.region'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('State/Region Name',required=True)
	types = fields.Selection([
							('state','State'),
							('region','Region')],string='Type')
	code = fields.Char('Code',required=True)

# CITY
class HrCity(models.Model):
	_name = 'hr.city'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('City Name',required=True)
	code = fields.Char('Code',required=True)
	region_id = fields.Many2one('hr.region',string='Region',required=True)

# TOWNSHIP
class HrTownship(models.Model):
	_name = 'hr.township'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Township Name',required=True)
	code = fields.Char('Township Code',required=True)
	city_id = fields.Many2one('hr.city',string='City')
	district_id = fields.Many2one('hr.district',string='District')

# DISTRICT
class TownshipDistrict(models.Model):
	_name = 'hr.district'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('District Name',required=True)

# COUNTRY
class HrCountry(models.Model):
	_name = 'hr.country'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Country Name',required=True)
	country_code = fields.Char('Country Code',required=True)

# BUSINESS TYPE
class BusinessType(models.Model):
	_name = 'business.type'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name =  fields.Char('Business Type Name',required=True)

	_sql_constraints = [
	('_unique', 'unique (name)', 'No duplication of Business Type is allowed')
	]

# BUSINESS TYPE
class Floor(models.Model):
	_name = 'building.floor'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name =  fields.Char('Floor',required=True)

	_sql_constraints = [
	('_unique', 'unique (name)', 'No duplication of Floor is allowed')
	]

# INDUSTRY ZONE
class IndustryZone(models.Model):
	_name = 'industry.zone'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Industry Zone',required=True)

# BUSINESS UNIT
class BusinessUnit(models.Model):
	_name = 'business.unit'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char('Name')
	code = fields.Char('Code')
	business_unit_type_id = fields.Many2one('business.type', string='Type')
	company = fields.Char('Company')
	number = fields.Char('Number')
	building_floor_id = fields.Many2one('building.floor', string='Floor')
	building = fields.Char('Building')
	street = fields.Char('Street')
	zone = fields.Many2one('industry.zone')
	road = fields.Char('Road')
	quarter = fields.Char('Quarter')
	township_id = fields.Many2one('hr.township', string='Township')
	city_id = fields.Many2one('hr.city', string='City')
	division_id = fields.Many2one('hr.region', string='Division')
	country_id = fields.Many2one('hr.country', string='Country')
	country_code = fields.Char(string="Country code", related='country_id.country_code', readonly=True)
	active = fields.Boolean(string='Active', default=True)

	phone = fields.Char('Phone')
	mobile = fields.Char('Mobile')


	@api.onchange('city_id')
	def onchange_city_id(self):
		self.division_id = self.city_id.region_id.id
	
class HRemployee(models.Model):

	_inherit = 'hr.employee'
	bu_id = fields.Many2one('business.unit',string='Business Unit')

class HRemployeePublic(models.Model):

	_inherit = 'hr.employee.public'
	bu_id = fields.Many2one('business.unit',string='Business Unit')


class ResUsers(models.Model):
    _inherit = 'res.users'
    bu_id = fields.Many2one('business.unit',string='Business Unit')