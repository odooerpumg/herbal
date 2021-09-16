from odoo import models, fields

class OfficeLocation(models.Model):
	_name = 'office.location'

	name = fields.Char('Office Name')

# class BusinessUnits(models.Model):
#     _name = 'business.unit'
#     _inherit = ['mail.thread', 'mail.activity.mixin']

#     name = fields.Char('Name')
#     location_id = fields.Many2one('office.location',string='Office Location')

class Branch(models.Model):
    _name = 'business.branch'
    name = fields.Char('Name')