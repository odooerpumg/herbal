from odoo import models, fields, api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit',)

    
    @api.model
    def create(self, vals):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        # create view location for warehouse then create all locations
        loc_vals = {'name': _(vals.get('code')), 'usage': 'view',
                    'location_id': self.env.ref('stock.stock_location_locations').id}
        if vals.get('company_id'):
            loc_vals['company_id'] = vals.get('company_id')
        vals['view_location_id'] = self.env['stock.location'].create(loc_vals).id
        sub_locations = self._get_locations_values(vals)

        for field_name, values in sub_locations.items():
            values['location_id'] = vals['view_location_id']
            if vals.get('company_id'):
                values['company_id'] = vals.get('company_id')
            if vals.get('business_unit_id'):
                values['business_unit_id'] = vals.get('business_unit_id')
            print("VALUES", values)
                
            vals[field_name] = self.env['stock.location'].with_context(active_test=False).create(values).id
            
        result = super(StockWarehouse, self).create(vals)
    
        return result
    


class StockLocation(models.Model):
    _inherit = 'stock.location'

    business_unit_id = fields.Many2one('business.unit', string='Business Unit')
    


    

    
