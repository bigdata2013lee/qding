(function($) {

    var mm = qd.ns("views.talk");

    /**
     * 门口机列表
     * @type {any}
     */
    mm.GatesView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/talk/tpls/gates.tpl',

        _query_pager:{
            page_no:1, page_size:12
        },

        initialize: function () {
            this._gates = [];
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.query_gates();
        },

        events: {
            "click div.query_box .query_btn":function (evt) {
                this.query_gates();
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.query_gates();
            }
          /*  ,
            'change select': function(evt){
                this.query_gates();
            }*/
        },

        query_gates:function () {
            var self = this;
            var params = qd.utils.serialize(".query_box>form");
            qd.rpc("gate.GateApi.list_project_gates", $.extend({project_id:select_project_id, pager:self._query_pager}, params))
            .success(function (result) {
                self.$el.find(".data_list_box").render_template(result);
                self._gates = result.data.collection ||  [];
            });
        },
    });


})(jQuery);