from odoo import models, fields, api
from datetime import date,timedelta,datetime
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError,UserError
import odoo.addons.decimal_precision as dp
import time
from odoo.tools.translate import _
import calendar
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth
import hashlib
import json
import requests
import locale
from odoo.tools import float_is_zero, float_compare, safe_eval, date_utils, email_split, email_escape_char, email_re
from odoo.tools.misc import formatLang, format_date, get_lang


class AccountPayment(models.Model):
	_inherit = 'account.payment'

	payment_type = fields.Selection([
		('outbound', 'Send Money'), ('inbound', 'Receive Money'), 
		('transfer', 'Internal Transfer'), ('br_bu', 'BR to BU Transfer')], string='Payment Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
	# transfer_journal_id = fields.Many2one('account.journal',string="Transfer To", required=True)
	approve_person_id = fields.Many2one('hr.employee',string='Approval Person')
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	internal_transfer_type = fields.Selection([
		('journal_to_journal', 'Journal to Journal'), ('journal_to_account', 'Journal to Account'), 
		('account_to_journal', 'Account to Journal')], string='Internal Transfer Type')
	petty_cash_id = fields.Many2one('petty.cash.expense',stirng='Petty Cash')

	def post(self):
		""" Create the journal items for the payment and update the payment's state to 'posted'.
			A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
			and another in the destination reconcilable account (see _compute_destination_account_id).
			If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
			If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
		"""
		AccountMove = self.env['account.move'].with_context(default_type='entry')
		for rec in self:

			if rec.state != 'draft':
				raise UserError(_("Only a draft payment can be posted."))

			if any(inv.state != 'posted' for inv in rec.invoice_ids):
				raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

			# keep the name in case of a payment reset to draft
			if not rec.name:
				# Use the right sequence to set the name
				if rec.payment_type == 'transfer':
					sequence_code = 'account.payment.transfer'
				else:
					if rec.partner_type == 'customer':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.customer.invoice'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.customer.refund'
					if rec.partner_type == 'supplier':
						if rec.payment_type == 'inbound':
							sequence_code = 'account.payment.supplier.refund'
						if rec.payment_type == 'outbound':
							sequence_code = 'account.payment.supplier.invoice'
				# rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
				seq = self.env['ir.sequence'].next_by_code('account.payment')
				seq_code = self.sequence
				rec.name = str(seq_code)+seq
				if not rec.name and rec.payment_type != 'transfer':
					raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

			moves = AccountMove.create(rec._prepare_payment_moves())
			moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

			# Update the state / move before performing any reconciliation.
			move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
			rec.write({'state': 'posted', 'move_name': move_name})

			if rec.payment_type in ('inbound', 'outbound'):
				# ==== 'inbound' / 'outbound' ====
				if rec.invoice_ids:
					(moves[0] + rec.invoice_ids).line_ids \
						.filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id and not (line.account_id == line.payment_id.writeoff_account_id and line.name == line.payment_id.writeoff_label))\
						.reconcile()
			elif rec.payment_type == 'transfer':
				# ==== 'transfer' ====
				moves.mapped('line_ids')\
					.filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
					.reconcile()

class ResCompany(models.Model):
	_name = 'res.company'
	_inherit = 'res.company'

	code = fields.Char('Code', required=True)

class AccountJournal(models.Model):
	_inherit = 'account.journal'

	def name_get(self):
		res = []
		for journal in self:
			currency = journal.currency_id or journal.company_id.currency_id
			name = "%s (%s)" % (journal.name, journal.code)
			res += [(journal.id, name)]
		return res