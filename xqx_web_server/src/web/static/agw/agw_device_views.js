(function($) {

    var mm = qd.ns("views.agw");
    mm.DeviceView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/agw/tpls/device.tpl',

        _query_pager:{
        },

        initialize: function () {
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.$el.find(".query_box>form").qd_phase_build_select();
            this.list_agw_devices();
        },

        events: {
            "click button.query_btn":function (evt) {
                var self = this;
                self.list_agw_devices();
            },
            "click a[name=alarm_areas_btn]":function (evt) {
                var self = this;
                var oid = $(evt.target).closest("tr").data("oid");
                self.get_agw(oid);
            },
            "click #alarm_areas_window .submit_btn":function (evt) {
                var self = this;
                self.set_agw_alarm_areas_enable();
            },
            "click .status": function(evt){
                var $target = $(evt.target);
                if($target.hasClass("toLeft")){
                    $target.removeClass("toLeft").addClass("toRight");
                }else{
                    $target.removeClass("toRight").addClass("toLeft");
                }
                setTimeout(function(){
                    if($target.hasClass("toLeft")){
                        $target.parent().removeClass("bg1").addClass("bg2").attr("data-value","false");
                    }else{
                        $target.parent().removeClass("bg2").addClass("bg1").attr("data-value","true");
                    }

                }, 50);
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.list_agw_devices();
            }
        },

        list_agw_devices:function () {
            var self = this;
            var params = $.extend({project_id: select_project_id}, qd.utils.serialize(".query_box>form"));
            qd.rpc("agw.AGWDeviceQueryApi.list_agw_devices",  $.extend({pager: self._query_pager}, params)).success(function (result) {
                $(self.el).find(".data_list_box").render_template(result);
            });
        },
        get_agw:function (oid) {
            var self = this;
            qd.rpc("agw.AGWDeviceQueryApi.get_agw", {agw_id:oid}).success(function (result) {
                self.$el.find("#alarm_areas_window .modal-body").render_template(result);
            });
        },

        set_agw_alarm_areas_enable:function () {
            var mbody = this.$el.find("#alarm_areas_window .modal-body");
            var items = [];
            $("#alarm_areas_window .modal-body div.wrap").each(function(evt){
                var name = $(this).attr("data-name");
                if(/alarm_(\d)/.test(name)){
                    var item = [RegExp.$1 * 1, $(this).attr("data-value") == "true" ];
                    items.push(item);
                }
            });

            var _params = qd.utils.serialize(mbody), params = {'agw_id':_params.agw_id, items:items};

           /*for(var key_name in _params){
                if(/alarm_(\d)/.test(key_name)){
                    params.items.push([RegExp.$1 * 1, qd.utils.val2boolean(_params[key_name])]);
                }
            }*/

            qd.rpc("agw.AGWDeviceApi.set_agw_alarm_areas_enable", params);
        }

    });

})(jQuery);