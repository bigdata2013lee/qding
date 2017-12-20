
var timer = {};
var qr_pass_data_view, app_order_data_view, base_data_view, device_monitoring_view,
    data_statistics_view, device_binding_view, new_card_view, user_card_view, failed_pass_data_view;
(function(){
    // 设置选中的小区
    function setArea(obj) {
        $("#communityName").html(obj.html());
        $("#sProvince").html(obj.attr("data-province"));
        $("#sCity").html(obj.attr("data-city"));
        $("#sCommunity").html(obj.attr("data-community"));
        $("#sProjectId").html(obj.attr("data-project-id"));
    }
    // 判断用户类型
    function checkUserType() {
        var type = $("#userType").html();
        if(/^3/.test(type)){
            var str = '.bind-phone, .export-btn, .monitor-manage{ display:none}';
            addCssByStyle(str);
        }
    }
    // 动态创建css
    function addCssByStyle(cssString){  
        var doc=document;  
        var style=doc.createElement("style");  
        style.setAttribute("type", "text/css");  
      
        if(style.styleSheet){// IE  
            style.styleSheet.cssText = cssString;  
        } else {// w3c  
            var cssText = doc.createTextNode(cssString);  
            style.appendChild(cssText);  
        }  
        document.getElementsByTagName("head")[0].appendChild(style); 
    } 
    // 设置小区信息
    var len = $("#selectCurrentCommunity a").size();
    if(len > 0){
        var firstItem = $("#selectCurrentCommunity a").eq(0);
        setArea(firstItem);
    }
    // 绑定选择小区事件
    $("#selectCurrentCommunity .search-li").on("click",function(event){
        event.stopPropagation();
    });

    $("#selectCurrentCommunity input[name=search_box_value]").on('keyup',function(){
        console.info("keyup");
        var search_box_value = $(this).val();
        var li_list = $("#selectCurrentCommunity li.community_li");
        li_list.each(function(){
            var community = $(this).text();
            if(community.indexOf(search_box_value) == -1){
                $(this).hide();
            }else{
                $(this).show();
            }
        });
    });

    $("#selectCurrentCommunity .clear-search-box-btn").on("click", function(){
        $("#selectCurrentCommunity input[name=search_box_value]").val("");
        $("#selectCurrentCommunity input[name=search_box_value]").keyup();
    });

    $("#selectCurrentCommunity").on("click", "a", function () {
        setArea($(this));
        var url = window.location.href;
        if(url.indexOf("brake_qr_pass_data") > 0){
            qr_pass_data_view.loadData();
        }
        if(url.indexOf("brake_app_order_data") > 0){
            app_order_data_view.loadData();
        }
        if(url.indexOf("base_data") > 0){
            base_data_view.loadData();
        }
        if(url.indexOf("device_monitoring") > 0){
            device_monitoring_view.loadData();
        }
        if(url.indexOf("data_statistics") > 0){
            data_statistics_view.loadData();
        }
        if(url.indexOf("device_binding") > 0){
            device_binding_view.loadData();
        }
        if(url.indexOf("card_new") > 0){
            new_card_view.loadData();
        }
        if(url.indexOf("card_user") > 0){
            user_card_view.loadData();
        }
        if(url.indexOf("failed_pass_data") > 0){
            failed_pass_data_view.loadData();
        }
    });
//    checkUserType();
})();

var AppRouter = Backbone.Router.extend({
    content: '.brake-content',

    loading_page: function() {
        $(this.content).html('<center style="padding:150px 0px;"><i class="fa fa-spinner fa-spin text-muted" style="font-size:45px;"></i></center>');
        for (var item in timer) {
            !!item && clearInterval(timer[item]);
        }
        timer = {};
    },

    load_sentry_geo_selector: function(province_selector,city_selector,init_province,init_city) {
        $(province_selector).html('<option value="">-- 请选择 --</option>');
        $(city_selector).html('<option value="">-- 请选择 --</option>');
        
        $(province_selector).change(function() {
            $(city_selector).html('<option value="">-- 请选择 --</option>');
            $(city_selector).change();

            if ($(province_selector).val() == '') {
                return true;
            }    

            $.ajax({
                url: ' /geo_api/Geo_Api/get_city_list/',
                type: 'POST',
                data: {
                    province: $(province_selector).val()
                },   
                dataType: 'json',
                success: function(result) {
                    var city_list = result.data.city_list;

                    for (var i=0;i<city_list.length;i++) {
                        var option = $('<option></option>');
                        option.attr('value',city_list[i] || $(province_selector).val());
                        option.html(city_list[i] || $(province_selector).val());
                        $(city_selector).append(option);
                    }

                    !!init_city && $(city_selector).val(init_city);
                }
            });
        });

        $.ajax({
            url: ' /geo_api/Geo_Api/get_province_list/',
            type: 'POST',
            data: { },
            dataType: 'json',
            success: function(result) {
                var province_list = result.data.province_list;

                for (var i=0;i<province_list.length;i++) {
                    var option = $('<option></option>');
                    option.attr('value',province_list[i]);
                    option.html(province_list[i]);
                    $(province_selector).append(option);
                }
                !!init_province && $(province_selector).val(init_province);
            }
        });
    },    

    routes: {
        '': function() {
            var manage_index_view = Backbone.View.extend({
                className: 'manage-index-view',
                template: CONST.static_url+'community/ejs/manage_index_block.html',

                initialize: function() {
                    $(this.el).html(new EJS({url: this.template}).render({})); 
                }

            });

            this.loading_page();
            var view = new manage_index_view(); 
            $(this.content).html(view.el);
        },

        'edit_admin_profile': function() {
            this.loading_page();
            var view = new edit_admin_profile_view();
            $(this.content).html(view.el);
            $('input[name="gender"]').bootstrapSwitch();
        },

        'brake_qr_pass_data': function() {
            this.loading_page();
            var view = qr_pass_data_view = new brake_qr_pass_data_view(); 
            $(this.content).html(view.el);
        },

        'brake_app_order_data': function() {
            this.loading_page();
            var view = app_order_data_view = new brake_app_order_data_view(); 
            $(this.content).html(view.el);
        },

        'modify_password': function() {
            this.loading_page();
            var view = new modify_password_view(); 
            $(this.content).html(view.el);
        },
        'device_monitoring':function(){
        	this.loading_page();
        	var view = device_monitoring_view = new brake_device_monitoring_view();
        	$(this.content).html(view.el);
        },
        'device_binding':function(){
            this.loading_page();
            var view = device_binding_view = new brake_device_binding_view();
            $(this.content).html(view.el);
        },
        'monitor_manage':function(){
            this.loading_page();
            var view = new brake_monitor_manage_view();
            $(this.content).html(view.el);
        },
        'data_statistics':function(){
            this.loading_page();
            var view = data_statistics_view = new brake_data_statistics_view();
            $(this.content).html(view.el);
        },
        'search_data/by_phone':  function(){
            var view = new qd.Views.DataSearchByPhoneView();
            $(this.content).html(view.el);
        },
        'search_data/by_machine':  function(){
            var view = new qd.Views.DataSearchByMachineView();
            $(this.content).html(view.el);
        },
        'search_data/by_card': function(){
            var view = new qd.Views.DataSearchByCardView();
            $(this.content).html(view.el);
        },
        'card_new': function(){
            this.loading_page();
            var view = new_card_view = new card_new_view();
            $(this.content).html(view.el);
        },
        'card_user': function(){
            this.loading_page();
            var view = user_card_view = new card_user_view();
            $(this.content).html(view.el);
        },
        'search_data/failed_pass_data': function(){
            var view = failed_pass_data_view = new qd.Views.DataSearchFailedPassDataView();
            $(this.content).html(view.el);
        },
    }
});

var app_router = new AppRouter();
Backbone.history.start();








