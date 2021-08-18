odoo.define('pos_action_button.ActionButton', function (require) {
"use strict";

// require pos screens
var pos_screens = require('point_of_sale.screens');

/* ------------ SET UMGian Price ------------ */
// create a new button by extending the base ActionButtonWidget
var UmgianButton = pos_screens.ActionButtonWidget.extend({
    template: 'UmgianButton',
    
    init: function(parent) {
        this._super(parent);
        var self = this;
        this.order = this.pos.get_order();   
        this.selected_orderline = this.order.get_selected_orderline();
    },

    get_umgian_price(){
        if(this.selected_orderline){
            return this.selected_orderline.get_product().umgian_price      
        }
    },

    get_umgian_family_price(){        
        if(this.selected_orderline){
            return this.selected_orderline.get_product().umgian_family_price   
        }           
    },

    get_selected_orderline(){        
        return this.selected_orderline
    },

    button_click: function(){
        var self = this;
        // console.log("self",self.$el);
        // console.log("this.$", this.$("#set_umgian_price"));
        var order = self.pos.get_order();        
        var selected_orderline = order.get_selected_orderline();
        if(selected_orderline){
            // console.log("umgian_price",selected_orderline.get_product().umgian_price); 
            // console.log("umgian_family_price",selected_orderline.get_product().umgian_family_price);
            selected_orderline.price_manually_set = true;
            selected_orderline.set_unit_price(order.get_selected_orderline().get_product().umgian_price);
        }
    }, 

});

/* ------------ SET UMGian Family Price ------------ */
// create a new button by extending the base UmgianButton
var UmgianFamilyButton = UmgianButton.extend({
    template: 'UmgianFamilyButton',

    button_click: function(){
        var self = this;
        // console.log("self",self.$el);
        // console.log("this.$", this.$("#set_umgian_price"));
        var order = self.pos.get_order();        
        var selected_orderline = order.get_selected_orderline();
        if(selected_orderline){
            // console.log("umgian_price",selected_orderline.get_product().umgian_price); 
            // console.log("umgian_family_price",selected_orderline.get_product().umgian_family_price);
            selected_orderline.price_manually_set = true;
            selected_orderline.set_unit_price(order.get_selected_orderline().get_product().umgian_family_price);
        }
    },
    
});

// define the UmgianFamilyButton button
pos_screens.define_action_button({
    'name': 'UmgianFamilyButton',
    'widget': UmgianFamilyButton,
    'condition': function(){return this.pos;},
});

// define the UmgianButton button
pos_screens.define_action_button({
    'name': 'UmgianButton',
    'widget': UmgianButton,
    'condition': function(){return this.pos;},
});

});