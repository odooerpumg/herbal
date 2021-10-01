# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.AbstractModel):
    _inherit = 'res.users'
    pos_session_id = fields.Many2one('pos.config', string='Pos Session ID')

class PosConfig(models.Model):
    _inherit = 'pos.config'

    cashier_ids = fields.One2many('res.users', 'pos_session_id', string='Cashiers')
