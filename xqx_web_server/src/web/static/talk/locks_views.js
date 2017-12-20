

(function($) {

    var mm = qd.ns("views.talk");

    /**
     * 通话记录列表
     * @type {any}
     */
    mm.LocksView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/talk/tpls/locks.tpl',

        _query_pager:{
            page_no:1, page_size:12
        },

        initialize: function () {
            this._locks = [];
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.$el.find(".query_box>form").qd_phase_build_select();
            this.query_locks();
        },

        events: {
            "click div.query_box .query_btn":function (evt) {
                this.query_locks();
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.query_locks();
            }
           /* ,
            'change select': function(evt){
                this.query_locks();
            }*/
        },

        query_locks:function () {
            var self = this;
            var params = qd.utils.serialize(".query_box>form");

            Object.keys(params).forEach(function(item){
                if(item == "phase_no" || item == "building_no"){
                    params[item] =  params[item] * 1;
                }

            });

            qd.rpc("qdtalk.GateOpenLockRecordApi.query_for_wuye", $.extend({pager:self._query_pager}, params))
                .success(function (result) {
                    self.$el.find(".data_list_box").render_template(result);
                    self._locks = result.data.collection ||  [];
                });
        },
    });


})(jQuery);