odoo.define('pos_action_button.customer', function (require) {

"use strict";
    
// require pos screens
var pos_screens = require('point_of_sale.screens');

var core = require('web.core');
var QWeb = core.qweb;

var rpc = require('web.rpc');
// var _super_ClientListScreenWidget = pos_screens.ClientListScreenWidget.prototype;
pos_screens.ClientListScreenWidget.include({

    testing_fun: function(){
        return "This is return data from 'testing_fun' method"
    },

    // Shows,hides or edit the customer details box :
    // visibility: 'show', 'hide' or 'edit'
    // partner:    the partner object to show or edit
    // clickpos:   the height of the click on the list (in pixel), used
    //             to maintain consistent scroll.
    display_client_details: function(visibility,partner,clickpos){
        var self = this;
        // console.log("POS", self.pos);
        var searchbox = this.$('.searchbox input');
        var contents = this.$('.client-details-contents');
        var parent   = this.$('.client-list').parent();
        var scroll   = parent.scrollTop();
        var height   = contents.height();

        contents.off('click','.button.edit'); 
        contents.off('click','.button.save'); 
        contents.off('click','.button.undo'); 
        contents.on('click','.button.edit',function(){ self.edit_client_details(partner); });
        contents.on('click','.button.save',function(){ self.save_client_details(partner); });
        contents.on('click','.button.undo',function(){ self.undo_client_details(partner); });
        this.editing_client = false;
        this.uploaded_picture = null;

        if(visibility === 'show'){
            contents.empty();
            contents.append($(QWeb.render('ClientDetails',{widget:this,partner:partner})));

            var new_height   = contents.height();

            if(!this.details_visible){
                // resize client list to take into account client details
                parent.height('-=' + new_height);

                if(clickpos < scroll + new_height + 20 ){
                    parent.scrollTop( clickpos - 20 );
                }else{
                    parent.scrollTop(parent.scrollTop() + new_height);
                }
            }else{
                parent.scrollTop(parent.scrollTop() - height + new_height);
            }

            this.details_visible = true;
            this.toggle_save_button();
        } else if (visibility === 'edit') {
            // Connect the keyboard to the edited field
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                contents.off('click', '.detail');
                searchbox.off('click');
                contents.on('click', '.detail', function(ev){
                    self.chrome.widget.keyboard.connect(ev.target);
                    self.chrome.widget.keyboard.show();
                });
                searchbox.on('click', function() {
                    self.chrome.widget.keyboard.connect($(this));
                });
            }

            this.editing_client = true;
            contents.empty();
            contents.append($(QWeb.render('ClientDetailsEdit',{widget:this,partner:partner})));
            this.toggle_save_button();

            // Browsers attempt to scroll invisible input elements
            // into view (eg. when hidden behind keyboard). They don't
            // seem to take into account that some elements are not
            // scrollable.
            contents.find('input').blur(function() {
                setTimeout(function() {
                    self.$('.window').scrollTop(0);
                }, 0);
            });

            contents.find('.client-address-country').on('change', function (ev) {
                var $stateSelection = contents.find('.client-address-states');
                var value = this.value;
                $stateSelection.empty()
                $stateSelection.append($("<option/>", {
                    value: '',
                    text: 'None',
                }));
                self.pos.states.forEach(function (state) {
                    if (state.country_id[0] == value) {
                        $stateSelection.append($("<option/>", {
                            value: state.id,
                            text: state.name
                        }));
                    }
                });
            });

            contents.find('.client-customer-type').on('change', function (ev) {
                var $umgIdBlockSelection = contents.find('.umgian-id-block');
                var value = this.value;
                $umgIdBlockSelection.empty()
                if(value === 'umgian'){
                    var val_check = (("umgian_employee_id" in partner === true) ? partner.umgian_employee_id : '')
                    console.log("partner.umgian_employee_id",partner.umgian_employee_id);
                    $umgIdBlockSelection.append(
                        `<span class='label' width="24">UMGian ID</span>
                        <input class='detail client_umgian_employee_id' name="umgian_employee_id"  value="`+ 
                        ( (val_check !== false) ? val_check : '')
                        +`"></input>
                        `
                    )
                }else if(value === 'umgian_family_member'){
                    contents.find('.client_umgian_employee_id').val('');
                }else{
                    contents.find('.umgian-id-block').empty();
                }

                var $umgBuBlockSelection = contents.find('.umgian-bu-block');
                $umgBuBlockSelection.empty()
                if(value === 'umgian'){
                    var $bu_options = `<option value=''>None</option>`
                    var bu_check = (("business_unit_id" in partner === true) ? true : false)
                    $.each(self.pos.business_units, function(key,value) {
                        if(bu_check){
                            if (partner.business_unit_id[0] === value['id']){
                                $bu_options += `<option selected='1' value='`+ value['id'] +`'>`+value['name']+`</option>`
                            }else{
                                $bu_options += `<option value='`+ value['id'] +`'>`+value['name']+`</option>`
                            } 
                        }else{
                            $bu_options += `<option value='`+ value['id'] +`'>`+value['name']+`</option>`
                        }
                        
                    });
                    $umgBuBlockSelection.append(
                        `<span class='label'>Business Unit</span>
                         <select class='detail client-business-unit needsclick' name='business_unit_id'>
                                   ` +$bu_options+`                      
                         </select>`
                    );
                }else if(value !== 'umgian'){
                    contents.find('.umgian-bu-block').empty();
                }else{
                    contents.find('.umgian-bu-block').empty();
                }
                
                
            });
                        
            contents.find('.client-nrc-no').on('change', function (ev) {
                var $descriptionSelection = contents.find('.client-nrc-description');
                var value = this.value;
                $descriptionSelection.empty()
                $descriptionSelection.append($("<option/>", {
                    value: '',
                    text: 'None',
                }));
                self.pos.nrc_description.forEach(function (desc) {
                    if (desc.nrc_no_id[0] == value) {
                        $descriptionSelection.append($("<option/>", {
                            value: desc.id,
                            text: desc.name
                        }));
                    }
                });
            });            

            contents.find('.image-uploader').on('change',function(event){
                if (event.target.files.length) {
                    self.load_image_file(event.target.files[0],function(res){
                        if (res) {
                            contents.find('.client-picture img, .client-picture .fa').remove();
                            contents.find('.client-picture').append("<img src='"+res+"'>");
                            contents.find('.detail.picture').remove();
                            self.uploaded_picture = res;
                        }
                    });
                }
            });
        } else if (visibility === 'hide') {
            contents.empty();
            parent.height('100%');
            if( height > scroll ){
                contents.css({height:height+'px'});
                contents.animate({height:0},400,function(){
                    contents.css({height:''});
                });
            }else{
                parent.scrollTop( parent.scrollTop() - height);
            }
            this.details_visible = false;
            this.toggle_save_button();
        }
    },

    // what happens when we save the changes on the client edit form -> we fetch the fields, sanitize them,
    // send them to the backend for update, and call saved_client_details() when the server tells us the
    // save was successfull.
    save_client_details: function(partner) {
        var self = this;

        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            if (self.integer_client_details.includes(el.name)){
                var parsed_value = parseInt(el.value, 10);
                if (isNaN(parsed_value)){
                    fields[el.name] = false;
                }
                else{
                    fields[el.name] = parsed_value
                }
            }
            else{
                fields[el.name] = el.value || false;
            }
        });

        if (!fields.name) {
            this.gui.show_popup('error',_t('A Customer Name Is Required'));
            return;
        }

        if (this.uploaded_picture) {
            fields.image_1920 = this.uploaded_picture;
        }

        fields.id = partner.id || false;

        var contents = this.$(".client-details-contents");
        contents.off("click", ".button.save");

        if(jQuery.inArray("customer_type", fields) && fields["customer_type"] === false){
            fields["umgian_employee_id"] = false
            fields["business_unit_id"] = false
        }
        rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [fields],
            })
            .then(function(partner_id){
                self.saved_client_details(partner_id);
            }).catch(function(error){
                error.event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
                contents.on('click','.button.save',function(){ self.save_client_details(partner); });
            });
    },

});

});