# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryExt(http.Controller):
#     @http.route('/inventory_ext/inventory_ext/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_ext/inventory_ext/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_ext.listing', {
#             'root': '/inventory_ext/inventory_ext',
#             'objects': http.request.env['inventory_ext.inventory_ext'].search([]),
#         })

#     @http.route('/inventory_ext/inventory_ext/objects/<model("inventory_ext.inventory_ext"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_ext.object', {
#             'object': obj
#         })
