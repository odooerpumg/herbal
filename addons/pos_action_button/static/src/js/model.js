odoo.define('pos_action_button.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            this.reload_debts_partner_ids = [];
            // TODO: should be replaced with native Promise
            this.reload_debts_timer = $.when();
            models.load_fields('product.product', ['umgian_price', 'umgian_family_price']);
            models.load_fields('res.partner', [
                'birthdate_date', 'age', 'customer_type', 
                'referee_name', 'referee_number',
                'sec_contact_name', 'sec_contact_number',
                'medical_history',  'remark',
            ]);
            _super_posmodel.initialize.apply(this, arguments);
        },
    });
    
    models.Product = models.Product.extend({
        get_umgian_price: function() {
            var self = this;
            var umgian_price = self.umgian_price;
            return umgian_price
        },
        get_umgian_family_price(){
            var self = this;
            var umgian_family_price = self.umgian_family_price;
            return umgian_family_price
        }
    });

    models.Order = models.Order.extend({
        select_orderline: function(line){
            if(line){
                if(line !== this.selected_orderline){
                    if(this.selected_orderline){
                        this.selected_orderline.set_selected(false);
                    }
                    this.selected_orderline = line;
                    this.selected_orderline.set_selected(true);
                    
                }
            }else{
                this.selected_orderline = undefined;
            }            
        },        
    });
});