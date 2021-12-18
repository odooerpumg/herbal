# -*- coding: utf-8 -*-
from odoo import models, fields, api

class import_pos_orders(models.TransientModel):
    _name = 'posorder.import'
    _description = 'import_pos_orders'

    name = fields.Char()
    session_id = fields.Many2one('pos.session', string='Session')
    orders_lists_file = fields.Binary(string='File' )

    def action_import(self):
        return True
