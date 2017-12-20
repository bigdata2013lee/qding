var base_data_view = Backbone.View.extend({
    template: versionify(CONST.static_url+'manage/ejs/base_data_block.html'),
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
        this.getList();
    },
    
    updateParam: function (status) {
        this.param = {};
        this.param.province = $(".search-province").val() || "";
        this.param.city = $(".search-city").val() || "";
        this.param.project = $(".search-project").val() || "";
        this.param.page_no = this.page_no;
        this.param.page_size = this.page_size;
        switch(status){
            case "1":
                this.param.group = $(".search-group").val() || "";
                this.param.build = $(".search-build").val() || "";
                this.param.unit = $(".search-unit").val() || "";
                this.param.room = $(".search-room-text").val() || "";
                this.param.room_id = $(".search-room-id-text").val() || "";
                break;
            case "2":
                this.param.outer_app_user_id = $(".search-outer-app-user-id-text").val() || "";
                this.param.app_user_id = $(".search-app-user-id-text").val() || "";
                this.param.phone = $(".search-app-user-phone-text").val() || "";
                break;
            default:
                break;
        }
    },
    
    getList: function (pageIndex) {
        var status = $(".search-status").val() || "0";
        switch(status){
            case "1":
                $('.search-apartment-div').removeClass('hide');
                $('.search-app-user-div').addClass('hide');
            	this.updateParam(status);
                this.getContentList(pageIndex, "/basedata_api/Basedata_Apartment_Api/get_apartment_by_filter/1/", "apartment");
                break;
            case "2":
                $('.search-app-user-div').removeClass('hide');
                $('.search-apartment-div').addClass('hide');
                this.updateParam(status);
                this.getContentList(pageIndex, "/basedata_api/Basedata_Bj_App_User_Api/get_app_user_by_filter/1/", "app_user");
                break;
            default:
                $('.search-apartment-div').addClass('hide');
                $('.search-app-user-div').addClass('hide');
            	this.updateParam(status);
                this.getContentList(pageIndex, "/basedata_api/Basedata_Project_Api/get_project_list_by_filter/", "project");
                break;
        }
    },

    getContentList:function(pageIndex, url, type){
        if(typeof pageIndex == "undefined"){
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;
        var field = type + "_list";
        var listUrl = "manage/ejs/base_data_list/" + type + ".html";
        $.ajax({
            url: url,
            type: 'POST',
            data:_this.param,   
            dataType: 'json',
            success: function(result) {
                if(result.data.flag === "Y"){
                    var ejs_html = new EJS({url: CONST.static_url + listUrl})
                                .render({list: result["data"][field], pagination: result.data.pagination});
                    $(_this.el).find('.base-data-list-block').html(ejs_html); 
                    if(!_this.page_inited){
                        _this.initPager(result.data.pagination.total_count);
                    }
                    var str='<button type="button" class="btn btn-info">总数：'+result.data.pagination.total_count+'</button>';
                    $('.base-data-count').html(str);
                }
            }
        });     
    },

    getSyncProjectList:function(){
        var project_html = "manage/ejs/base_data_list/sync_project.html";
        $.ajax({
            url:'/basedata_api/Basedata_Project_Api/find_project_by_name_from_bj/',
            type:'POST',
            data:{
                'project_name':$('.sync-project-name').val(),
            },
            dataType:'json',
            success: function (result) {
                if(result.data.flag='Y'){
                    var ejs_html=new EJS({url:CONST.static_url+ project_html}).render({
                        list:result.data.project_list
                    });
                    $('.base-data-sync-block').html(ejs_html);
                }
            }
        });
    },

    events: {
        'change .base-data-manage-type':function(){
            var manage_type = $(this.el).find('.base-data-manage-type').val();
            if (manage_type=='1'){
                $('.base-data-search, .base-data-list-block').removeClass("hide");
                $('.base-data-sync,.base-data-sync-block').addClass('hide');
                this.getList();
            }else{
                $('.base-data-search').addClass("hide");
                $('.base-data-list-block').addClass("hide");
                $('.base-data-sync').removeClass('hide');
                $('.base-data-sync-block').removeClass('hide');
                $('#pagination').html('');
            }
        },

        'change .search-city': function() {
            $('.search-project').html('<option value="">--楼盘--</option>');
            $('.search-project').val('');
            $('.project_select_input').val('');
            $('.search-project').change();

            if (!$('.search-city').val()) {
                return true;
            }
            
            $.ajax({
                url: '/basedata_api/Basedata_Project_Api/get_project_list_by_city/1/',
                type: 'POST',
                data: {
                    province: $('.search-province').val(),
                    city: $('.search-city').val()
                },   
                dataType: 'json',
                success: function(result) {
                    var project_list = result.data.project_list;
                    UI.createSimpleOption($('.search-project'), project_list);
                }
            });
        },
        
        'change .search-project': function() {
        	$('.search-group').html('<option value="">-- 组团 --</option>');
        	$('.search-group').val('');
        	$('.search-group').change();
        	
        	if (!$('.search-project').val()) {
        		return true;
        	}
        	
        	$.ajax({
        		url: '/basedata_api/Basedata_Group_Api/get_group_list/1/',
        		type: 'POST',
        		data: {
        			province: $('.search-province').val(),
        			city: $('.search-city').val(),
        			project: $('.search-project').val(),
        		},   
        		dataType: 'json',
        		success: function(result) {
        			var group_list = result.data.group_list;
        			UI.createSimpleOption($('.search-group'), group_list);
        		}
        	});
        },
        
        'change .search-group': function() {
        	$('.search-build').html('<option value="">-- 楼栋 --</option>');
        	$('.search-build').val('');
        	$('.search-build').change();
        	
        	$.ajax({
        		url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
        		type: 'POST',
        		data: {
        			province: $('.search-province').val(),
        			city: $('.search-city').val(),
        			project: $('.search-project').val(),
        			group: $('.search-group').val(),
        		},   
        		dataType: 'json',
        		success: function(result) {
        			var build_list = result.data.build_list;
        			UI.createSimpleOption($('.search-build'), build_list);
        		}
        	});
        },

        'keyup .search-room-text':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_list_timer);
            self.get_list_timer = setTimeout(function(){self.getList();},600)
        },

        'keyup .search-room-id-text':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_list_timer);
            self.get_list_timer =  setTimeout(function(){self.getList();},600);
        },

        'keyup .search-outer-app-user-id-text':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_list_timer);
            self.get_list_timer =  setTimeout(function(){self.getList();},600);
        },

        'keyup .search-app-user-id-text':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_list_timer);
            self.get_list_timer =  setTimeout(function(){self.getList();},600);
        },

        'keyup .search-app-user-phone-text':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_list_timer);
            self.get_list_timer =  setTimeout(function(){self.getList();},600);
        },

        'keyup .sync-project-name':function(){
            var self = this;
            self.page_inited = false;
            window.clearTimeout(self.get_sync_project_list_timer);
            self.get_sync_project_list_timer = setTimeout(function(){self.getSyncProjectList();},200)
        },

        'click .sync-base-data-search-btn':function(){
            this.getSyncProjectList();
        },

        'change .search-build': function() {
        	$('.search-unit').html('<option value="">-- 单元 --</option>');
        	$('.search-unit').val('');
        	$('.search-unit').change();
        	
        	if (!$('.search-build').val()) {
        		return true;
        	}
        	
        	$.ajax({
        		url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
        		type: 'POST',
        		data: {
        			province: $('.search-province').val(),
        			city: $('.search-city').val(),
        			project: $('.search-project').val(),
        			group: $('.search-group').val(),
        			build: $('.search-build').val(),
        		},   
        		dataType: 'json',
        		success: function(result) {
        			var unit_list = result.data.unit_list;
        			UI.createSimpleOption($('.search-unit'), unit_list);
        		}
        	});
        },

        'change .search-unit':function(){
        	this.getList();
        },
        
        'change .search-status':function(){
        	this.getList();
        },

        'click .search-base-data-btn':function(){
            this.getList();
        },


        'click .refresh-cache-btn':function(event){
            var item = $(event.srcElement || event.target).parents('tr.base-data-project-list');
            $.ajax({
                url:'/basedata_api/Basedata_Project_Api/refresh_project_data/1/',
                type:'POST',
                'data':{
                    project_id:item.data('project-id'),
                },
                'dataType':'json',
                'success':function(result){
                    if(result.data.flag=='Y'){
                        UI.showTips('info','刷新缓存成功');
                    }else{
                        UI.showTips('danger',result.msg);
                    }
                }
            });
        },

        'click .sync-app-user-btn': function(){
            $.ajax({
                url: '/basedata_api/Basedata_Bj_App_User_Api/update_all_user_room_and_door_list/',
                type: 'POST',
                data:{},
                dataType: 'json',
                'success':function(result) {
                    if (result.data.flag == 'Y') {
                        UI.showSucTip('刷新成功');
                    } else {
                        UI.showErrTip(result.msg);
                    }
                }
            });
        },

        'click .sync-project-data-btn': function (event) {
            var item = $(event.srcElement || event.target).parents('tr.sync-project-list');
            $.ajax({
                url:'/basedata_api/Basedata_Project_Api/sync_project_data/',
                type:'POST',
                'data':{
                    project_id:item.data('project-id'),
                },
                'dataType':'json',
                'success':function(result){
                    if(result.data.flag=='Y'){
                        UI.showSucTip('同步数据成功');
                    }else{
                        UI.showErrTip(result.msg);
                    }
                }
            });
        },

        'click .app-user-update-btn': function(event) {
            var item = $(event.currentTarget).closest('tr');
            var phone = item.data('app_user_phone');
            var self = this;
            $.ajax({
                url: '/basedata_api/Basedata_Bj_App_User_Api/set_app_user_room_list_now/',
                type: 'POST',
                data:{
                    phone: phone,
                },
                dataType: 'json',
                success:function(result){
                    if(result.data.flag=='Y'){
                        UI.showSucTip('同步数据成功');
                        self.getList();
                    }else{
                        UI.showErrTip(result.msg);
                    }
                }
            });
        },

        'click .project_select_input':function(evt){
            var ops = $(evt.target).siblings("select").find("option");
            var ul = $(evt.target).siblings("ul");
            ul.html("");
            var value = $(evt.target).val();
            $(ops).each(function(){
                if ($(this).val().indexOf(value) != -1) {
                    ul.append("<li>"+$(this).val()+"</li>")
                }
            });
            if(ul.find("li").size()==0){
                ul.hide();
            }else{
                ul.show();
            }
            if(!!!value){
                $(evt.target).siblings("select").val("");
                $(evt.target).siblings("select").change();
            }
        },

        'keyup .project_select_input':function(evt){
            var ops = $(evt.target).siblings("select").find("option");
            var ul = $(evt.target).siblings("ul");
            ul.html("");
            var value = $(evt.target).val();
            $(ops).each(function(){
                if ($(this).val().indexOf(value) != -1) {
                    ul.append("<li>"+$(this).val()+"</li>");
                }
            });
            if(ul.find("li").size()==0){
                ul.hide();
                $(evt.target).val("");
                $(evt.target).click();
            }else{
                ul.show();
            }

            if(!!!$(evt.target).val()){
                $(evt.target).siblings("select").val("");
                $(evt.target).siblings("select").change();
            }
        },

        'click':function(evt) {
            console.info($(evt.target).closest("ul.project_select_ul"));
            if($(evt.target).is(".project_select_input")){return}
            if($(evt.target).closest("ul.project_select_ul").size() == 0){
                $("ul.project_select_ul").hide();
            }
        },

        'click .project_select_ul>li':function(evt){
            var project = $(evt.target).text();
            $(".project_select_input").val(project);
            $(evt.target).parent("ul").siblings("select").val(project);
            $(evt.target).parent("ul").siblings("select").change();
            $(evt.target).parent("ul").html("").hide();
        },
    }
});

