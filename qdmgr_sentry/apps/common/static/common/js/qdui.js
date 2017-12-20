(function($){

    jQuery.fn.qdui_autocomplete_win = function(opts){
        opts = jQuery.extend({
            name:"123",
            callback:function(){return false;}
        },opts||{});

        function test(){
            console.info('test');
        }


        return this.each(function(){
            var self = this;
            $(this).delegate("input.s_input","keyup",function(evt){
                if(evt.keyCode != 13){return}
                var key_wolds = $(evt.currentTarget).val();
                self.qdui_search(key_wolds, $(evt.currentTarget).closest('.qdui_autocomplete'));
            });

            $(this).delegate(".qdui_autocomplete .list_div li","click",function(evt){
                $(self).trigger('select_item',  [evt.currentTarget]);
                $(self).closest('.modal').modal('hide');
            });



            this.qdui_search = function (key_wolds) {
                var self = this;
                var li_list = $(this).find('.qdui_autocomplete ul>li');

                var worlds = key_wolds.trim().replace(/\*\.\[\]\\/gi, "").split(/\s+/);
                console.info(worlds);
                var reg_list = [];
                for(var i=0;i<worlds.length;i++){
                    reg_list.push(new RegExp(worlds[i]));
                }
                li_list.each(function(){
                    $(this).removeClass('unselected');
                    if(worlds.length == 0){return}
                    var text = $(this).text();

                    for(var i=0; i<reg_list.length;i++){
                        if(!reg_list[i].test(text)){$(this).addClass('unselected');return;}
                    }
                });
            }
        });
    }









})(jQuery)
