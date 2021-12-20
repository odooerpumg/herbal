# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xlrd
import base64
class import_pos_orders(models.TransientModel):
    _name = 'posorder.import'
    _description = 'import_pos_orders'

    name = fields.Char()
    session_id = fields.Many2one('pos.session', string='Session')
    orders_lists_file = fields.Binary(string='File' )

    def action_import(self):
        header_fields = [
            'type', 'user_id', 'session_id', 'pos_reference', 'partner_id',
            'fiscal_position_id', 'line_product_id', 'line_qty',
            'line_price_unit', 'discount'
        ]
        model = self.env['pos.order']
    # 
        # data = {
        #     'user_id': 2,
        #     'session_id': 1,
        #     'lines': [
        #         [
        #             0, 0, 
        #             {
        #             'qty': 1,
        #             'price_unit': 170000,
        #             'price_subtotal': 170000,
        #             'price_subtotal_incl': 170000, 
        #             'discount': 0, 
        #             'product_id': 3,
        #             'tax_ids': [[6, False, []]],
        #             'pack_lot_ids': [],
        #             # 'name': 'Backlogs/0046'
        #             }
        #         ]        
        #     ],
        #     'pos_reference': 'Order BACKLOG',
        #     # 'sequence_number': 2,
        #     'partner_id': False,
        #     # 'date_order': '2021-12-18 02:47:37',
        #     'fiscal_position_id': False,
        #     'pricelist_id': 1,
        #     'amount_paid': 170000,
        #     'amount_total': 170000,
        #     'amount_tax': 0,
        #     'amount_return': 0,
        #     'company_id': 1,
        #     'to_invoice': False,
        #     'employee_id': None
        # }
        # result = model.create(data)
    # 
        data = []
        lines = base64.decodestring(self.orders_lists_file)
        wb = xlrd.open_workbook(file_contents=lines)
        sheet = wb.sheet_by_index(0)
        
        order = {}
        lines = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            if rowx > 1:
                if row[0].value == 'order':
                    order = {}
                    lines = []
                    order['user_id'] = row[1].value
                    order['session_id'] = row[2].value
                    order['pos_reference'] = row[3].value
                    order['partner_id'] = row[4].value
                    order['fiscal_position_id'] = False
                if row[0].value == 'line' and order:
                    line = [
                        0, 0,
                        {
                            'product_id': 3,
                            'qty': 1,
                            'price_unit': 170000,
                            'price_subtotal': 170000,
                            'price_subtotal_incl': 170000, 
                            'discount': 0, 
                            'tax_ids': [[6, False, []]],
                            'pack_lot_ids': [],
                            # 'name': 'Backlogs/0046'
                        }
                    ]
                    lines.append(line)
            print("ORDER",)
        return True

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, values):
        print("++++++++++>", values)
        result = super(PosOrder, self).create(values)
        return result