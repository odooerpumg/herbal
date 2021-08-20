from odoo import models, fields

class WorkLocation(models.Model):
	_name = 'work.location'

	name = fields.Char('Office Name')

class BusinessUnits(models.Model):
    _name = 'business.unit'

    name = fields.Char('Name')
    location_id = fields.Many2one('work.location',string='Office Location')

class Branch(models.Model):
    _name = 'business.branch'
    name = fields.Char('Name')