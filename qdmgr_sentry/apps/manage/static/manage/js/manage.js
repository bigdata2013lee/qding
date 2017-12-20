
var timer = {};

var AppRouter = Backbone.Router.extend({
    content: '.manage-content',

    loading_page: function() {
        $(this.content).html('<center style="padding:150px 0px;"><i class="fa fa-spinner fa-spin text-muted" style="font-size:45px;"></i></center>');
        for (var item in timer) {
            !!item && clearInterval(timer[item]);
        }
        timer = {};
    },

    load_sentry_geo_selector: function(province_selector,city_selector,init_province,init_city) {
        $(province_selector).html('<option value="">-- 省份 --</option>');
        $(city_selector).html('<option value="">-- 城市 --</option>');
        
        $(province_selector).change(function() {
            $(city_selector).html('<option value="">-- 城市 --</option>');
            $(city_selector).change();

            if ($(province_selector).val() == '') {
                return true;
            }    

            $.ajax({
                url: '/basedata_api/Basedata_Project_Api/get_city_list_by_province/1/',
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
            url: '/basedata_api/Basedata_Project_Api/get_province_list/1/',
            type: 'POST',
            data: { },
            dataType: 'json',
            success: function(result) {
                var province_list = result.data.province_list;
                if(province_list && province_list.length > 0){
                    for (var i=0;i<province_list.length;i++) {
                        var option = $('<option></option>');
                        option.attr('value',province_list[i]);
                        option.html(province_list[i]);
                        $(province_selector).append(option);
                    }
                }
                !!init_province && $(province_selector).val(init_province);
            }
        });
    },

    routes: {
        '': function() {
            var manage_index_view = Backbone.View.extend({
                className: 'manage-index-view',
                template: CONST.static_url+'manage/ejs/manage_index_block.html',

                initialize: function() {
                    $(this.el).html(new EJS({url: this.template}).render({})); 
                }
            });

            this.loading_page();
            var view = new manage_index_view(); 
            $(this.content).html(view.el);
        },
        'web_user_manage':function(){
        	this.loading_page();
        	var view=new web_user_manage_view();
        	$(this.content).html(view.el);
        },
        'edit_admin_profile': function() {
            this.loading_page();
            var view = new edit_admin_profile_view();
            $(this.content).html(view.el);
            $('input[name="gender"]').bootstrapSwitch();
        },
        'brake_machine_manage': function() {
            this.loading_page();
            var view = new brake_machine_manage_view(); 
            $(this.content).html(view.el);
            this.load_sentry_geo_selector('.add-brake-province','.add-brake-city','','');
            this.load_sentry_geo_selector('.search-brake-province','.search-brake-city','','');
        },
        'brake_upgrade_manage':function(){
        	this.loading_page();
        	var view=new brake_upgrade_manage_view();
        	$(this.content).html(view.el);
        },
        'base_data': function() {
            this.loading_page();
            var view = new base_data_view(); 
            $(this.content).html(view.el);
            this.load_sentry_geo_selector('.search-province','.search-city','','');
        },
        'scan_data':function(){
            this.loading_page();
            var view = new scan_data_view();
            $(this.content).html(view.el);
        },
        'app_open_diary': function() {
        	this.loading_page();
        	var view = new app_open_diary_view(); 
        	$(this.content).html(view.el);
        }, 
        'web_open_diary': function() {
        	this.loading_page();
        	var view = new web_open_diary_view(); 
        	$(this.content).html(view.el);
        	this.load_sentry_geo_selector('.search-province','.search-city','','');
        },
        'request_data': function() {
            this.loading_page();
            var view = new request_data_view();
            $(this.content).html(view.el);
        },
    }
});

var app_router = new AppRouter();
Backbone.history.start();


