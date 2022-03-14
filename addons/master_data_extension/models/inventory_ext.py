from odoo import models, fields, api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit',)

    @api.model
    def create(self, vals):
        warehouse = super(StockWarehouse, self).create(vals)
        # print("warehouse=======>", warehouse)
        sub_location_ids = self.env['stock.location'].search([
            ('location_id','=',warehouse.view_location_id.id)
        ])
        # print("view_location_id==>",  warehouse.view_location_id)
        # print("sub_location_ids===>", sub_location_ids)
        if warehouse.view_location_id:
            warehouse.view_location_id.write({'business_unit_id':vals.get('business_unit_id') })
        if sub_location_ids:
            sub_location_ids.write({'business_unit_id':vals.get('business_unit_id')})
        # print("business_unit_id", vals.get('business_unit_id'))
        return warehouse

class StockLocation(models.Model):
    _inherit = 'stock.location'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit')
    


    

    
