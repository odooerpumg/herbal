from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def unlink(self):
        def get_selection_label(self, object, field_name, field_value):
            return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])
        for rec in self:
            state = get_selection_label(self, 'sale.order', 'state', rec.state)
            picking_id = self.env['stock.picking'].search([('origin','=',self.name)])
            if picking_id:
                raise ValidationError("Cannot delete Sale Order that has been set to 'Delivery'." )
        return super(SaleOrderInherit, self).unlink()


