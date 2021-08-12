odoo.define('pos_action_button.customer', function (require) {

"use strict";
    
// require pos screens
var pos_screens = require('point_of_sale.screens');

pos_screens.ClientListScreenWidget.include({

    testing_fun: function(){
        return "This is return data from 'testing_fun' method"
    }

});

});