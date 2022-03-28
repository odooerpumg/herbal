# -*- coding: utf-8 -*-
from http import server
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import xlrd
import base64

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def custom_action_done_backlog(self,backlog_date=None):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'description_picking': ops.description_picking,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                    'restrict_partner_id': pick.owner_id.id,
                                                    'company_id': pick.company_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': backlog_date if backlog_date else fields.Datetime.now()})
        self._send_confirmation_email()

        # Stock Account Move date change
        move = self.env['account.move'].search([('ref', 'like', self.name)])
        move.sudo().write({'date':backlog_date}) 

        return True


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

    def create_picking(self):
        # print('create_picking=================',self.date_order)
        """Create a picking for each order and validate it."""
        Picking = self.env['stock.picking']
        # If no email is set on the user, the picking creation and validation will fail be cause of
        # the 'Unable to log message, please configure the sender's email address.' error.
        # We disable the tracking in this case.
        if not self.env.user.partner_id.email:
            Picking = Picking.with_context(tracking_disable=True)
        Move = self.env['stock.move']
        StockWarehouse = self.env['stock.warehouse']
        for order in self:
            if not order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu']):
                continue
            address = order.partner_id.address_get(['delivery']) or {}
            picking_type = order.picking_type_id
            return_pick_type = order.picking_type_id.return_picking_type_id or order.picking_type_id
            order_picking = Picking
            return_picking = Picking
            moves = Move
            location_id = picking_type.default_location_src_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = StockWarehouse._get_partner_locations()
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            if picking_type:
                message = _("This transfer has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
                picking_vals = {
                    'origin': '%s - %s' % (order.session_id.name, order.name),
                    'partner_id': address.get('delivery', False),
                    'user_id': False,
                    'date_done': order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                }
                pos_qty = any([x.qty > 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if pos_qty:
                    order_picking = Picking.create(picking_vals.copy())
                    print(order_picking.id,'order_picking = Picking.create(picking_vals.copy())=========>',order_picking.date_done)
                    print("stock picking status bar============>>",order_picking.state)
                    if self.env.user.partner_id.email:
                        order_picking.message_post(body=message)
                    else:
                        order_picking.sudo().message_post(body=message)
                neg_qty = any([x.qty < 0 for x in order.lines if x.product_id.type in ['product', 'consu']])
                if neg_qty:
                    return_vals = picking_vals.copy()
                    return_vals.update({
                        'location_id': destination_id,
                        'location_dest_id': return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                        'picking_type_id': return_pick_type.id
                    })
                    return_picking = Picking.create(return_vals)
                    if self.env.user.partner_id.email:
                        return_picking.message_post(body=message)
                    else:
                        return_picking.sudo().message_post(body=message)

            for line in order.lines.filtered(lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding)):
                moves |= Move.create({
                    'name': line.name,
                    'company_id': line.company_id.id,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': order_picking.id if line.qty >= 0 else return_picking.id,
                    'picking_type_id': picking_type.id if line.qty >= 0 else return_pick_type.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else return_pick_type != picking_type and return_pick_type.default_location_dest_id.id or location_id,
                })

            # prefer associating the regular order picking, not the return
            order.write({'picking_id': order_picking.id or return_picking.id})

            if return_picking:
                order._force_picking_done(return_picking)
            if order_picking:
                order._force_picking_done(order_picking)
                # print("order_picking--> state",order_picking.state)
                # print("order_picking--> date_done",order_picking.date_done)

            # when the pos.config has no picking_type_id set only the moves will be created
            if moves and not return_picking and not order_picking:
                moves._action_assign()
                moves.filtered(lambda m: m.product_id.tracking == 'none')._action_done()

        return True

    def _force_picking_done(self, picking):
        """Force picking in order to be set as done."""
        self.ensure_one()
        picking.action_assign()
        wrong_lots = self.set_pack_operation_lot(picking)
        if not wrong_lots:
            picking.custom_action_done_backlog(self.date_order)

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
