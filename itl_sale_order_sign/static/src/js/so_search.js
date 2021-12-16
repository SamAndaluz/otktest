odoo.define('itl_sale_order_sign.SOSearchMainMenu', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var Dialog = require('web.Dialog');
var Session = require('web.session');
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var _t = core._t;

var MainMenu = AbstractAction.extend({
    contentTemplate: 'so_search_template',

    events: {
        "click .button_so_search": function(){
            this.so_search();
        },
    },

    init: function(parent, action) {
        this._super.apply(this, arguments);
    },

    so_search: function(e) {
        var self = this;
        //e.preventDefault();
        
        console.log(sale_order);
        if ($( ".oe_sale_order_input" ).val()){
            $('.oe_sale_order_input').removeClass("o_field_invalid");
            var sale_order = $( ".oe_sale_order_input" ).val().toString();
        }else{
            $('.oe_sale_order_input').addClass("o_field_invalid");
            self.do_warn('Advertencia', 'El valor en el campo es invalido.');
            return;
        }
        
        ajax.jsonRpc("/itl_sale_order_sign/orders/", 'call', {
            'sale_order' : sale_order
        }).then(function (data) {
            var results = data['results'];
            var found_so = data['found_so'];
            var found_so_num = data['found_so_num'];
            
            if ('was_done' in data && data['was_done'] == true){
                self.do_warn('Advertencia', 'La orden de venta indicada ya fue entregada.');
                return;
            }
            var found_so_num = data['found_so_num'];
            
            if (!found_so){
                self.do_warn('Advertencia', 'No se encontró la orden de venta.');
                return;
            }
            if ((found_so && results.length == 0 && found_so_num == 1) || ('found_picking' in results[0] && !results[0].found_picking)){
                self.do_warn('Advertencia', 'La orden de venta indicada no está lista para entrega.');
                return;
            }
            if (found_so && results.length == 0 && found_so_num > 1){
                self.do_warn('Advertencia', 'Se encontró más de una orden de venta con el mismo número y aún no están listas para entrega.');
                return;
            }
            if (results.length == 1){
                var rst = results[0];
                self.do_notify('Éxito', 'Se encontró una orden de venta válida.');
                window.open(rst['share_url'],"_blank");
            }
        });
        /*
        rpc.query({
            model: 'sale.order',
            method: 'search_read',
            args: [[['name','=',sale_order]], ['name', 'id']],
        }).then(function (data) {
            console.log(data);
            if (data.length == 0){
                self.do_warn('Advertencia', 'No se encontró la orden de vernta.');
                return;
            }
            
            if (data.length > 1){
                self.do_warn('Advertencia', 'Se encontraron ' + data.length + ' ordenes de compra.');
                return;
            }
        });*/
        /*
        return this._rpc({
                model: 'stock.inventory',
                method: 'open_new_inventory',
            })
            .then(function(result) {
                self.do_action(result);
            });
            */
    },
});

core.action_registry.add('so_seach_main_menu', MainMenu);

return {
    MainMenu: MainMenu,
};

});
