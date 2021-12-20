from odoo import models, fields, api


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit',)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit')
    


    

    
