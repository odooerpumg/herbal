# -*- coding: utf-8 -*-
from http import server
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import xlrd
import base64

class ImportPosOrders(models.TransientModel):
    _name = 'posorder.import'
    _description = 'import_pos_orders'

    name = fields.Char()
    session_id = fields.Many2one('pos.session', string='Session')
    # config_id = fields.Many2one('pos.config', related='session_id.config_id', string='POS config')
    config_id = fields.Many2one('pos.config', string='POS config')
    
    # customer
    customer_included = fields.Boolean("Customer Included In Template." , default=True)
    partner_id = fields.Many2one('res.partner', string='Customer') 

    orders_lists_file = fields.Binary(string='File' )

    sample_template = fields.Char(string="Sample Template", default='http://localhost:8069/import_pos_orders/static/src/custom_import_pos_order_template.xlsx')
    
    @api.model
    def default_get(self, fields):
        res = super(ImportPosOrders, self).default_get(fields)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        res['sample_template'] = '%s/import_pos_orders/static/src/custom_import_pos_order_template.xlsx' % base_url
        return res
    
    def action_import(self):
        model = self.env['pos.order']
        payment_model = self.env['pos.make.payment']
        lines = base64.decodestring(self.orders_lists_file)
        wb = xlrd.open_workbook(file_contents=lines)
        sheet = wb.sheet_by_index(0)
        try:
            data = []
            order = {}
            lines = []
            self.config_id.open_session_cb()
            session_id = self.config_id.current_session_id
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
                        order['session_id'] = session_id.id
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
                                'name': 'Backlogs/Session-%s' % session_id.name
                            }
                        ]
                        lines.append(line)
            _ids = []
            for o in data:
                current_order = model.create(o)
                _ids.append(current_order.id) 
        except Exception as error:
            raise UserError(_(str(error)))
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
        # notify_success(self, message="Default message", title=None, sticky=False)
        # Import completed
        # records were successfully imported
        self.env.user.notify_success(message='%s records were successfully imported.' % str(len(_ids)), title='Import completed')        
        return action

class PayPosOrder(models.TransientModel):
    _name = 'posorder.payment'
    _description = 'Create payment records for selected orders.'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method')
    order_ids = fields.Many2many('pos.order', string='Selected Orders')
    backlogs_payment_date = fields.Datetime("Payment Date")
    def check(self):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print ticket.
        """
        self.ensure_one()

        orders = self.env['pos.order'].browse(self.env.context.get('active_ids', False))
        try:
            set_backlogs_payment_date = False
            pids = []
            for order in orders:
                if set_backlogs_payment_date == False:
                    order.session_id.write({'backlogs_payment_date': self.backlogs_payment_date})
                currency = order.currency_id

                init_data = {
                    'amount': order.amount_total,
                    'payment_name': self.payment_method_id.name,
                    'payment_method_id': self.payment_method_id.id,
                    'payment_date': self.backlogs_payment_date
                }
                if not float_is_zero(init_data['amount'], precision_rounding=currency.rounding):
                    payment = order.add_payment_for_backlogs_order({
                        'pos_order_id': order.id,
                        'amount': order._get_rounded_amount(init_data['amount']),
                        'name': init_data['payment_name'],
                        'payment_method_id': init_data['payment_method_id'],
                        'payment_date': init_data['payment_date']
                    })
                    if payment:
                        pids.append(payment.id)

                if order._is_pos_order_paid():
                    order.action_pos_order_paid()
            # notify_success(self, message="Default message", title=None, sticky=False)
            # Import completed
            # records were successfully imported
            self.env.user.notify_success(message='records were successfully created.', title='Create completed')
            # return {'type': 'ir.actions.act_window_close'}
            # Domain to filterout only current created order
            domain = [('id', 'in', pids)]
            action = {
                'name': _('Payments'),
                'type': 'ir.actions.act_window',
                'res_model': 'pos.payment',
                'view_type': 'list',
                'view_mode': 'list,form',
                'domain': domain,
            } 
            return action           
        except Exception as error:
            return UserError(_(error))

    @api.model
    def default_get(self, fields):
        res = super(PayPosOrder, self).default_get(fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        res['order_ids'] = active_ids
        return res

class PointOfSaleConfig(models.Model):
    _inherit = 'pos.config'

    back_logs = fields.Boolean("Backlog")
    business_unit = fields.Many2one('business.unit', string='Business Unit',)

class PosOrder(models.AbstractModel):

    _inherit = 'pos.order'
    
    def add_payment_for_backlogs_order(self, data):
        """Create a new payment for the Backlogs order"""
        self.ensure_one()
        payment = self.env['pos.payment'].create(data)
        self.amount_paid = sum(self.payment_ids.mapped('amount'))   
        return payment 

class PosPayment(models.AbstractModel):

    _inherit = 'pos.payment'    
    backlogs_payment_date = fields.Datetime("Payment Date")

class PosSessions(models.Model):
    _inherit = 'pos.session'
    backlogs_payment_date = fields.Datetime("Payment Date")

    def _create_account_move(self):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - creating and validating account.bank.statement for cash payments
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """
        journal = self.config_id.journal_id
        # Passing default_journal_id for the calculation of default currency of account move
        # See _get_default_currency in the account/account_move.py.
        account_move = self.env['account.move'].with_context(default_journal_id=journal.id).create({
            'journal_id': journal.id,
            'date': self.backlogs_payment_date if self.backlogs_payment_date else fields.Date.context_today(self),
            'ref': self.name,
        })
        self.write({'move_id': account_move.id})

        data = {}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)
        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        data = self._create_extra_move_lines(data)
        data = self._create_balancing_line(data)
        data = self._reconcile_account_move_lines(data)

    def _get_statement_line_vals(self, statement, receivable_account, amount, date=False, partner=False):
        return {
            'date': self.backlogs_payment_date,
            'amount': amount,
            'name': self.name,
            'statement_id': statement.id,
            'account_id': receivable_account.id,
            'partner_id': partner and self.env["res.partner"]._find_accounting_partner(partner).id
        }
