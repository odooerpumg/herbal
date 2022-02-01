# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
# from datetime imsort datetime, time, timedelta
# from pytz imsort timezone, UTC


class SaleCommission(models.Model):
	_inherit = 'account.move'

	product_uom_id = fields.Many2one('uom.uom', string='UOM')
	journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,states={'draft': [('readonly', False)]}, domain="[('company_id', '=', company_id)]",)