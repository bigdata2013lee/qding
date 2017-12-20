
var brake_app_order_data_view = Backbone.View.extend({
    className: 'brake_app_order_data_view',
    template: versionify(CONST.static_url+'community/ejs/brake_app_order_data_block.html'),
    status: null,
    page_no: 1,
    page_size: 30,
    page_inited:false,
    
    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
        var view = this;
        this.status = $(this.el).find('.qr-data-status').val();
        this.page_no = 1;
        this.page_size = 30;
        $(this.el).find('.dump-excel-date').datetimepicker({
            language:  'zh-CN',
            todayBtn:  1,
            autoclose: 1,
            todayHighlight: 1,
            startView: 2,
            minView: 2,
            maxView: 4,
            forceParse: 0,
            showMeridian: 1,
            format: 'yyyy-mm-dd',
            linkField: 'alarm_start_date',
            linkFormat: 'yyyy-mm-dd',
            initialDate: new Date(),
        });
        this.loadData();
    },
    loadData: function () {
        this.getList();
    },
    getList:function(pageIndex){
        if(typeof pageIndex == "undefined"){
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;
        $.ajax({
            url: '/sentry_api/Sentry_Visitor_Api/get_visitor_list/1/',
            type: 'POST',
            data: {
                coming: _this.status,
                page_no: _this.page_no,
                page_size: _this.page_size,
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html()
            },   
            dataType: 'json',
            success: function(result) {
                if (result.data.flag == 'Y'){
                    var ejs_html = new EJS({url: CONST.static_url+'community/ejs/app_data_list_block.html?'+Math.random()})
                                    .render({app_data_list: result.data.app_data_list});
                    $(_this.el).find('.app-data-list-block').html(ejs_html);
                    if(result.data.pagination){
                        if(!_this.page_inited){
                            _this.initPager(result.data.pagination.total_count);
                        }
                    }
                }
            }
        });    	
    },

    // 分页
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
    events: {
    	// 'click .search-app-data-btn':function(event){
    	// 	var search = $(event.srcElement || event.target).parents('.search-app-data');
    	// 	this.page_no=search.data("page-no");
    	// 	this.page_size=search.data("page-size");
    	// 	this.getList();
    	// },
        'change .qr-data-status':function(event){
        	this.status= $('.qr-data-status').val();
        	this.page_no=1;
        	this.page_size=50;
        	this.getList();
        },
        
       'click .brake-dump-excel-btn':function(){
//   		 $('#dump-data-option').modal('show');
            $("#dump_data_modal span.dump_data_type").text('brake_order');
            $('#dump_data_modal').modal('show');
   		},
   		
   		'click .submit-dump-excel-btn':function(event){
	   		if( !$('.start-time').val() || !$('.end-time').val()){
                UI.showTips('danger','请填写完整信息');
	   			return false;
	   		}
            var modal = $(event.srcElement || event.target).parents('#dump-data-option');
            var start_time = new Date($('.start-time').val()).getTime()/1000;
            var end_time = new Date($('.end-time').val()).getTime()/1000;
            if(start_time >= end_time) {
                UI.showTips('danger', '结束时间必须比开始时间晚');
                return false;
            }
            var data =  {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                start_time: start_time,
                end_time: end_time,
            };
            var get_str = $.param(data);
            var url = '/dump_order_list_to_excel?'+ get_str;
            modal.modal('hide');
            window.location.href = url;
   		}
    }
});

