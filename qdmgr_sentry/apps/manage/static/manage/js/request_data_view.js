var request_data_view = Backbone.View.extend({
    template: versionify(CONST.static_url+'manage/ejs/request_data_block.html'),
    page_no: 1,
    page_size: 30,
    page_inited:false,
    param: {},
    get_list_timer:0,
    get_sync_project_list_timer:0,
    initialize: function() {
        $(this.el).html(new EJS({ url: this.template }).render({}));
        var view = this;
        view.loadData();
    },

    initPager:function(total){
        var _this = this;
        $('#pagination').pagination(total,{
            num_edge_entries: 1, //边缘页数
            num_display_entries: 4, //主体页数
            callback: function (pageIndex, jq) {
              if(_this.page_inited){
                _this.page_no = pageIndex + 1;
                _this.getList(_this.page_no);
              }
            },
            items_per_page: _this.page_size, //每页显示1项
            prev_text: "«",
            next_text: "»"
        });
        this.page_inited = true;
    },

    loadData: function () {
        this.getDayRequestCount();
    },

    getDayRequestCount:function(){
        $.ajax({
            url: '/common_api/User_Request_Api/get_day_request_count/',
            type: 'POST',
            data: {},
            dataType: 'json',
            success: function(result) {
                if(result.data.flag === "Y"){
                    $('.day-request-count').html(result.data.request_count+"次");
                }
            }
        });
    },

    events: {
    },

});