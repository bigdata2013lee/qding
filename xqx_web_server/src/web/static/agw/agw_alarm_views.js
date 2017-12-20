(function($) {

    var mm = qd.ns("views.agw");

    mm.AlarmView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/agw/tpls/alarm.tpl',

        _query_pager:{
        },

        initialize: function () {
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.$el.find(".query_box>form").qd_phase_build_select();
            this.list_agw_alarms();
        },

        events: {
            "click button.query_btn":function (evt) {
                this.list_agw_alarms();
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.list_agw_alarms();
            }
        },

        list_agw_alarms:function () {
            var self = this;
            var params = $.extend({project_id: select_project_id, pager:self._query_pager}, qd.utils.serialize(".query_box>form"));
            params.phase_no  = parseInt(params.phase_no*1);
            params.building_no = parseInt(params.building_no*1);
            qd.rpc("agw.AlarmApi.list_alarms", params).success(function (result) {
                $(self.el).find(".data_list_box").render_template(result);
            });
        }

    });

})(jQuery);