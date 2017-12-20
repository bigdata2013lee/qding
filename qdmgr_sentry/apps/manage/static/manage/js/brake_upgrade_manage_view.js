
var brake_upgrade_manage_view = Backbone.View.extend({
    className: 'brake-upgrade-manage-view',
    template: versionify(CONST.static_url+'manage/ejs/brake_upgrade_manage_block.html'),
    addIndex: 1,
    province_list: [],
    city_list: [],
	project_list: [],

    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
        this.getVersionList();
        this.getProvince();
    },

    getVersionList:function(){
    	var view=this;
    	$.ajax({
    		url: '/brake_api/Brake_Version_Api/get_brake_version_list/',
    		type: 'POST',
    		data: {},
    		dataType: 'json',
    		success: function(result){
    			version_list=result.data.version_list;
    			$(view.el).find('.upgrade-list').html(new EJS({url:CONST.static_url+'manage/ejs/brake_version_list.html?'+Math.random()})
    					.render({version_list:result.data.version_list}));
    		}
    	});
    },

    getVersionSettingList:function(){
        var view=this;
        $.ajax({
            url: '/brake_api/Brake_Config_Version_Api/get_version_list/1/',
            type: 'POST',
            data: {},
            dataType: 'json',
            success: function(result){
                version_list=result.data.version_list;
                $(view.el).find('.upgrade-list').html(new EJS({url:CONST.static_url+'manage/ejs/brake_version_setting_list.html?'+Math.random()})
                        .render({version_list:result.data.version_list}));
            }
        });
    },

	// 创建绑定小区列表
	createproject: function() {
		var str='';
		str += '<div style="margin-top:0.5em" class="mb15 relative select-project-list add-project-list col-xs-8 col-xs-offset-3" id="project_'+ this.addIndex +'">\
			<div class="col-xs-3">\
				<select class="form-control version-target-province" name="province">\
					<option value="">--省份--</option>\
				</select>\
			</div>\
			<div class="col-xs-3">\
				<select class="form-control version-target-city" name="city">\
					<option value="">--城市--</option>\
				</select>\
			</div>\
			<div class="col-xs-3">\
				<select class="form-control version-target-project" name="project" style="display:none">\
					<option value="">--楼盘--</option>\
				</select>\
				<input type="text" autocomplete="off" data-outer_project_id="" value="" placeholder="--楼盘--" class="form-control project_select_input"  name="search_box_value"/>\
                <ul class="project_select_ul"></ul>\
			</div>\
			<div class="col-xs-3">\
			    <a class="btn btn-default btn-small del-project-btn" title="删除绑定">删除绑定</a>\
			</div>\
		</div>';
		return str;
	},

	getProvince: function() {
	    var _this = this;
		$.ajax({
			url:' /basedata_api/Basedata_Project_Api/get_province_list/',
			type:'POST',
			data:{
			},
			dataType:'json',
			context: this,
			success:function(result){
				_this.province_list = result.data.province_list;
                                var str=""
                                str +='<option value="">--省份--</option>'
                                for(i=0;i<this.province_list.length;i++){
                                    str += '<option value="' + this.province_list[i] + '">' + this.province_list[i] + '</option>';
                                }
				$('#userProvince').html("").append(str);
			}
		});
	},

    getTargetProject: function() {
        var div_list = $(".target-project>div");
        div_list_length = div_list.length;

        var target_project_list = [];

        div_list.each(function(){
            var select_province = $(this).find("select[name='province']");
            var province = select_province.val();

            var select_city = $(this).find("select[name='city']");
            var city = select_city.val();

            var input_project = $(this).find("input");
            var project = input_project.val();
            var outer_project_id = input_project.data("outer_project_id");

            if(!province && !city && !project && div_list_length==1){ return false}

            if(outer_project_id){
                target_project = {
                    "province": province,
                    "city": city,
                    "project": project,
                    "outer_project_id": outer_project_id,
                    "project_flag": province+city+project,
                }
                if(!qd.utils.valueInDictList(outer_project_id, "outer_project_id", target_project_list)){
                    target_project_list.push(target_project);
                }else{
                    target_project_list = 123;
                    UI.showErrTip("请勿重复选择社区");
                    return false;
                }
            }else{
                target_project_list = 123;
                UI.showErrTip("请选择社区");
                return false;
            }
        });

        console.info(target_project_list);
        return target_project_list;
    },

    events: {
        'click .add-project-btn':function(){
			$("#bindingProject").parent().append(this.createproject());
			var $province = $("#project_"+ this.addIndex).find(".version-target-province");
			UI.createSimpleOption($province, this.province_list);
			this.addIndex++;
		},

		// 删除绑定小区
		'click .del-project-btn':function(event){
			$(event.srcElement || event.target).parent().parent().remove();
		},

        'change .change-type':function(){
            var val = $('.change-type').val();
            if(val === "1"){
                this.getVersionSettingList();
                $(".target-project").addClass("hide");
                $(".lowest-version").addClass("hide");
            }else{
                this.getVersionList();
                $(".target-project").removeClass("hide");
                $(".lowest-version").removeClass("hide");
            }
        },


		'change .version-target-province':function(event){
			var parentWrap = $(event.srcElement || event.target).parent().parent();
			var city = parentWrap.find('.version-target-city');
			var project = parentWrap.find('.version-target-project');

			var province_val = $(event.srcElement || event.target).val();

            city.empty();
			city.html('<option value="">--城市--</option>');
			city.val('');
			city.change()

			if(!province_val){
				return false;
			}

			$.ajax({
				url: '/basedata_api/Basedata_Project_Api/get_city_list_by_province/',
				type: 'POST',
				data: {
					province: province_val
				},
				dataType: 'json',
				context: this,
				success: function(result) {
					UI.createSimpleOption(city, result.data.city_list);
				}
			});
		},

		'change .version-target-city':function(event){
			var parentWrap = $(event.srcElement || event.target).parent().parent();

			var province = parentWrap.find('.version-target-province');
			var city = parentWrap.find('.version-target-city');
			var project = parentWrap.find('.version-target-project');

            project.empty()
			project.html('<option value="">--楼盘--</option>');
			project.val("");

			var city_val = city.val();
			var province_val = province.val();

			if(!city_val || !province_val){
			    return false;
			}


			$.ajax({
				url:'/basedata_api/Basedata_Project_Api/get_project_list_by_filter/',
				type:'POST',
				data:{
					province:province_val,
					city: city_val,
				},
				dataType:'json',
				context: this,
				success:function(result){
				    UI.createOption(project, result.data.project_list, "outer_project_id", "project", "");
				}
			});
		},

        'click .project_select_input':function(evt){
            var ops = $(evt.target).siblings("select").find("option");
            var ul = $(evt.target).siblings("ul");
            ul.html("");
            var value = $(evt.target).val();
            $(ops).each(function(){
                if ($(this).html().indexOf(value) != -1) {
                    ul.append("<li data-outer_project_id="+$(this).val()+">"+$(this).html()+"</li>");
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
                $(evt.target).data("outer_project_id", "");
            }
        },

        'keyup .project_select_input':function(evt){
            var ops = $(evt.target).siblings("select").find("option");
            var ul = $(evt.target).siblings("ul");
            ul.html("");
            var value = $(evt.target).val();
            $(ops).each(function(){
                if ($(this).html().indexOf(value) != -1) {
                    ul.append("<li data-outer_project_id="+$(this).val()+">"+$(this).html()+"</li>");
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
                $(evt.target).data("outer_project_id", "");
            }
        },

        'click':function(evt) {
            if($(evt.target).is(".project_select_input")){return}
            if($(evt.target).closest("ul.project_select_ul").size() == 0){
                $("ul.project_select_ul").hide();
            }
        },

        'click .project_select_ul>li':function(evt){
            var project = $(evt.target).text();
            var outer_project_id = $(evt.target).data('outer_project_id');
            $(evt.target).parent("ul").siblings("input").val(project);
            $(evt.target).parent("ul").siblings("input").data("outer_project_id", outer_project_id);
            $(evt.target).parent("ul").siblings("select").val(project);
            $(evt.target).parent("ul").html("").hide();
        },
    	
        'click .brake-upgrade-btn': function() {
            target_project_list = this.getTargetProject();
            if(target_project_list == 123){ return false}
            $(".version-project-list").val(JSON.stringify(target_project_list));
            var _this = this, url = "";
        	if(!$('.brake-upgrade-version').val() ||
        			!$('.brake-upgrade-file').val()){
                UI.showTips('danger', '请填写完整的信息');
        		return false;
        	}
            if($('.brake-upgrade-former-version').val()==$('.brake-upgrade-version').val()){
                UI.showTips('danger', '新版本号不可以与旧版本号相同');
                return false;
            }
            var val = $('.change-type').val();
            if(val === "1"){
                url = "/manage/add_brake_config_version/";
            } else {
                url = "/manage/add_brake_version/";
            }
            $('.brake-upgrade-form').ajaxSubmit({
                url: url,
                type: 'POST', 
                dataType: 'json',
                success: function(result) {
                    var text = "发布升级包成功";
                    if (result.data.flag == 'N') {
                        text = result.msg;
                    }
                    UI.showTips('info', text);
            		val === "1" ? _this.getVersionSettingList() : _this.getVersionList();
                }
            });
        },

        'click .remove-version-btn': function(event) {
            if (!confirm('确定要删除吗？')) return true;
            var _this = this;
            var item = $(event.srcElement || event.target).parents('tr.version-item');
            var val = $('.change-type').val();
            if(val === "1"){
                url = "/manage/remove_brake_version/";
            } else {
                url = "/manage/remove_version/";
            }
            $.ajax({
                url: url,
                type: 'POST',
                data: {
                	version_id: item.data('version-id'),
                    file_uri: item.data('version-fileuri')
                },   
                dataType: 'json',
                success: function(result) {
                    var text = "删除成功";
                    if (result.data.flag === "N") {
                        text = result.msg;
                    }
                    UI.showTips('info', text);
                    val === "1" ? _this.getVersionSettingList() : _this.getVersionList();
                }
            });
        },
    }
});

