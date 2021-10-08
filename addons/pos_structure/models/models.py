# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit = 'res.users'
    pos_session_id = fields.Many2one('pos.config', string='Pos Session ID')

class PosConfig(models.Model):
    _inherit = 'pos.config'

    cashier_ids = fields.One2many('res.users', 'pos_session_id', string='Cashiers', domain="[('pos_session_id', '=', False)]")
    
    cashier_count = fields.Integer(string="Assigned cashier", compute="_compute_cashiers_list")

    @api.depends('cashier_ids')
    def _compute_cashiers_list(self):
        for record in self:
            record.cashier_count = len(record.cashier_ids)
    