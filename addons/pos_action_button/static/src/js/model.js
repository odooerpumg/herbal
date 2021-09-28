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
                'medical_history',  'remark', 'umgian_employee_id',
                'nrc_no','nrc_desc','nrc_type','nrc_number',
                'business_unit_id','branch_id'
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

    // At POS Startup, load the New Models, and add them to the pos model

    // nrc.no
    models.load_models({
        model: 'nrc.no',
        fields: ['name'],
        loaded: function(self,nrc_keys){
            self.nrc_keys = nrc_keys;
        },
    });
    // nrc.desc
    models.load_models({
        model: 'nrc.description',
        fields: ['name', 'nrc_no_id'],
        loaded: function(self,nrc_description){
            self.nrc_description = nrc_description;
        },
    }); 
    // nrc.type   
    models.load_models({
        model: 'nrc.type',
        fields: ['name', 'description'],
        loaded: function(self,nrc_types){
            self.nrc_types = nrc_types;
        },
    });

    // business.unit
    models.load_models({
        model: 'business.unit',
        fields: ['name', 'country_id', 'division_id', 'city_id', 'township_id'],
        loaded: function(self,business_units){
            self.business_units = business_units;
        },
    });

    // business.branch
    models.load_models({
        model: 'business.branch',
        fields: ['name'],
        loaded: function(self,business_branches){
            self.business_branches = business_branches;
        },
    });

    // office.location
    models.load_models({
        model: 'office.location',
        fields: ['name'],
        loaded: function(self,office_locations){
            self.office_locations = office_locations;
        },
    });

});