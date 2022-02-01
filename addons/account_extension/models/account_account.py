from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountAccount(models.Model):
	_inherit = 'account.account'

	bu_br_name = fields.Char('BU/BR Name')
	parent_id = fields.Many2one('account.account',string='Parent Code')
	is_sub = fields.Boolean('Is Sub',default=False)

	@api.onchange('parent_id')
	def onchange_parent_id(self):
		if self.parent_id:
			self.is_sub = True