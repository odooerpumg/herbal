odoo.define('js_framework_sample.SampleFramework', function(require){
    'use strict';
    var Screens = require("point_of_sale.screens")
    var core = require('web.core');
    var _t = core._t;
    var models = require('point_of_sale.models');
    Screens.ActionpadWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
                var order = self.pos.get_order();
                console.log("ORDER",order.get_total_balance());
                alert("ORDER", order.get_total_balance())
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    self.gui.show_popup('confirm',{
                        'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                        confirm: function(){
                            self.gui.show_screen('payment');
                        },
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        }        
    });
});