odoo.define('hide_action_buttons.hide_action_buttons', function (require) {
    "use strict";
    var core = require('web.core');
    var BasicView = require('web.BasicView');

    var _t = core._t;
    var QWeb = core.qweb;
    console.log("--> cargando...");
    BasicView.include({
        init: function(viewInfo, params) {
            console.log('--> JS loaded...');  
            this._super.apply(this, arguments);
            
            this.recordID = params.recordID;
            this.model = params.model;
            console.log("---> record: " + this.recordID);
            console.log("---> model: " + this.model);
            
        }, 
        _loadData: function (model) {
            console.log('--> JS load_record...'); 
            console.log("--> ok...");
            if (this.recordID) {
                // Add the fieldsInfo of the current view to the given recordID,
                // as it will be shared between two views, and it must be able to
                // handle changes on fields that are only on this view.
                model.addFieldsInfo(this.recordID, {
                    fields: this.fields,
                    fieldsInfo: this.fieldsInfo,
                });

                var record = model.get(this.recordID);
                var viewType = this.viewType;
                var viewFields = Object.keys(record.fieldsInfo[viewType]);
                var fieldNames = _.difference(viewFields, Object.keys(record.data));
                var fieldsInfo = record.fieldsInfo[viewType];

                //console.log("---> record: ", record);


                if (this.model=='res.partner'){
                    if (record.hide_action_button){
                        this.$buttons.find('.o_form_button_edit').css({"display":"none"});
                    }
                    else{
                        this.$buttons.find('.o_form_button_edit').css({"display":""});
                    }
                }
            }
            
            return this._super.apply(this, arguments);
        }
        
    });
    
});