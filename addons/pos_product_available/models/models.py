# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    show_qtys = fields.Boolean(
        "Show Product Qtys", help="Show Product Qtys in POS", default=True
    )
    default_location_src_id = fields.Many2one(
        "stock.location", related="picking_type_id.default_location_src_id"
    )
    avaliable_product_ids = fields.Many2many('product.product', string='Products', compute='_compute_avaliable_product_ids')

    @api.depends('default_location_src_id')
    def _compute_avaliable_product_ids(self):
        quant_model = self.env['stock.quant']
        for record in self:
            stock_quant = quant_model.search([('location_id', '=', record.default_location_src_id.id)])
            _p_ids = []
            for rec in stock_quant:
                _p_ids.append(rec.product_id.id)
            record.avaliable_product_ids = _p_ids

    # TESTING: FAIL
    def compute_avaliable_product_qty_by_location(self):
        quant = self.env['stock.quant']
        product = self.env['product.product'].search([('id', '=', 9)])
        location = self.env['stock.location'].search([('id', '=', 25)])
        result = quant._get_available_quantity(product,location)
        return result
