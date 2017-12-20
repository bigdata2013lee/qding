
(function($) {

    var mm = qd.ns("views.talk");

    /**
     * 通话记录列表
     * @type {any}
     */
    mm.CallsView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/talk/tpls/calls.tpl',

        _query_pager:{
            page_no:1, page_size:12
        },

        initialize: function () {
            this._calls = [];
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.$el.find(".query_box>form").qd_phase_build_select();
            this.query_calls();
        },

        events: {
            "click div.query_box .query_btn":function (evt) {
                this.query_calls();
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.query_calls();
            },
            'change select': function(evt){
                this.query_calls();
            }
        },

        query_calls:function () {
            var self = this;
            var params = qd.utils.serialize(".query_box>form");
			params.phase_no = parseInt(params.phase_no*1);
			params.building_no = parseInt(params.building_no*1);
            Object.keys(params).forEach(function(item){
                if(item == "phase_no" || item == "building_no"){
                    params[item] =  params[item] * 1;
                }

            });
            qd.rpc("qdtalk.CallRecordApi.query_for_wuye", $.extend({pager:self._query_pager}, params))
                .success(function (result) {
                    self.$el.find(".data_list_box").render_template(result);
                    self._calls = result.data.collection ||  [];
                });
        },
    });


})(jQuery);