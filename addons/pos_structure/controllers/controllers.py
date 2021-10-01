# -*- coding: utf-8 -*-
# from odoo import http


# class PosStructure(http.Controller):
#     @http.route('/pos_structure/pos_structure/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_structure/pos_structure/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_structure.listing', {
#             'root': '/pos_structure/pos_structure',
#             'objects': http.request.env['pos_structure.pos_structure'].search([]),
#         })

#     @http.route('/pos_structure/pos_structure/objects/<model("pos_structure.pos_structure"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_structure.object', {
#             'object': obj
#         })
