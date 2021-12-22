# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import xlrd
import base64
class import_pos_orders(models.TransientModel):
    _name = 'posorder.import'
    _description = 'import_pos_orders'

    name = fields.Char()
    session_id = fields.Many2one('pos.session', string='Session')
    config_id = fields.Many2one('pos.config', related='session_id.config_id', string='POS config')
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method')
    
    # customer
    customer_included = fields.Boolean("Customer Included In Template." , default=True)
    partner_id = fields.Many2one('res.partner', string='Customer') 

    orders_lists_file = fields.Binary(string='File' )

    def action_import(self):
        header_fields = [
            'type', 'user_id', 'session_id', 'pos_reference', 'partner_id',
            'fiscal_position_id', 'line_product_id', 'line_qty',
            'line_price_unit', 'discount'
        ]
        model = self.env['pos.order']
        payment_model = self.env['pos.make.payment']
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
                # ENDING FLAG
                if row[0].value == 'end':
                    if order and lines:
                        order['lines'] = lines
                        data.append(order)    
                                    
                # ORDER
                elif row[0].value == 'order':
                    if order and lines:
                        order['lines'] = lines
                        data.append(order)
                        order = {}
                        lines = []
                    order['user_id'] = self.env.user.id
                    order['session_id'] = self.session_id.id
                    order['pos_reference'] = row[1].value

                    if self.customer_included:
                        order['partner_id'] = row[2].value
                    else:
                        order['partner_id'] = self.partner_id.id

                    order['amount_total'] = row[3].value
                    order['amount_paid'] = row[3].value
                    order['date_order'] = row[4].value

                    order['fiscal_position_id'] = False
                    order['amount_tax'] = 0
                    order['amount_return'] = 0
                
                # ORDER LINE ITEMS
                elif row[0].value == 'line' and order:
                    line = [
                        0, 0,
                        {
                            'product_id': int(row[5].value),
                            
                            # PRICE
                            'qty': int(row[6].value),
                            'price_unit': float(row[7].value),
                            'price_subtotal': int(row[6].value) * float(row[7].value),
                            'price_subtotal_incl': int(row[6].value) * float(row[7].value),

                            'discount': float(row[8].value), 
                            'tax_ids': [[6, False, []]],
                            'pack_lot_ids': [],
                            'name': 'Backlogs/Session-%s' % self.session_id.name
                        }
                    ]
                    lines.append(line)
        _ids = []
        for o in data:
            current_order = model.create(o)
            _ids.append(current_order.id)
            # if current_order:
            #     current_order.add_payment({
            #                     'pos_order_id': current_order.id,
            #                     'amount': current_order._get_rounded_amount(init_data['amount']),
            #                     'name': init_data['payment_name'],
            #                     'payment_method_id': self.payment_method.id,
            #                 })  
        
        # Domain to filterout only current created order
        domain = [('id', 'in', _ids)]
        action = {
            'name': _('Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'domain': domain,
        }
        return action

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, values):
        result = super(PosOrder, self).create(values)
        return result