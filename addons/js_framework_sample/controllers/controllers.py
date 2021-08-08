# -*- coding: utf-8 -*-
# from odoo import http


# class JsFrameworkSample(http.Controller):
#     @http.route('/js_framework_sample/js_framework_sample/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/js_framework_sample/js_framework_sample/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('js_framework_sample.listing', {
#             'root': '/js_framework_sample/js_framework_sample',
#             'objects': http.request.env['js_framework_sample.js_framework_sample'].search([]),
#         })

#     @http.route('/js_framework_sample/js_framework_sample/objects/<model("js_framework_sample.js_framework_sample"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('js_framework_sample.object', {
#             'object': obj
#         })
