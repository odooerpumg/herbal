# -*- coding: utf-8 -*-
# from odoo import http


# class ImportPosOrders(http.Controller):
#     @http.route('/import_pos_orders/import_pos_orders/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/import_pos_orders/import_pos_orders/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('import_pos_orders.listing', {
#             'root': '/import_pos_orders/import_pos_orders',
#             'objects': http.request.env['import_pos_orders.import_pos_orders'].search([]),
#         })

#     @http.route('/import_pos_orders/import_pos_orders/objects/<model("import_pos_orders.import_pos_orders"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('import_pos_orders.object', {
#             'object': obj
#         })
