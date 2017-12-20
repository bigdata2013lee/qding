var web_user_manage_view=Backbone.View.extend({
	className: 'web_user_manage_view',
	template: versionify(CONST.static_url+'manage/ejs/web_user_manage_block.html'),
	getUserListTimer:0,
	addIndex: 1,
	province_list: [],
	city_list: [],
	project_list: [],
	selected_project : [],
	userList: [],
	page_no:1,
	page_size:10,
	page_inited:false,

	initialize:function(){
		$(this.el).html(new EJS({url:this.template}).render({}));
		this.getUserList();
		this.getProvince();
		this.page_no=1;
		this.page_size=10;

		window.current_view = this;
	},

    initPager:function(total){
        var _this = this;
        $('#pagination').pagination(total,{
            num_edge_entries: 1, //边缘页数
            num_display_entries: 4, //主体页数
            callback: function (pageIndex, jq) {
              if(_this.page_inited){
                _this.page_no = pageIndex + 1;
                _this.getUserList(_this.page_no);
              }
            },
            items_per_page: _this.page_size, //每页显示1项
            prev_text: "«",
            next_text: "»"
        });
        this.page_inited = true;
    },

	getUserList: function () {
		var _this=this;
		$.ajax({
			url: '/user_api/Web_User_Api/get_web_user_by_filter/',
			type: 'post',
			dataType: 'json',
			data: {
				role:$('.search-user-role').val(),
				access:$('.search-user-access').val(),
				username:$('.search-username').val(),
				phone:$('.search-phone').val(),
				page_no:_this.page_no,
				page_size:_this.page_size,
			},
			context: this,
            success: function(result) {
            	if (result.data.flag !== "Y") {
	            	UI.showTips('danger', result.msg);
                    return false;
	            }
	            var ejs_html = new EJS({url: CONST.static_url+'manage/ejs/web_user_list_block.html?'+Math.random()}).render({web_user_list: result.data.web_user_list});
            	$('.web-user-list-block').html(ejs_html); 
            	_this.userList = result.data.web_user_list;
            	var str='<button type="button" class="btn btn-info">总数：'+result.data.pagination.total_count+'</button>';
            	$('.user_count').html(str);
				if (result.data.pagination && result.data.web_user_list.length>0){
					if(!_this.page_inited){
						_this.initPager(result.data.pagination.total_count);
					}
				}else{
					$('#pagination').html('');
				}
            }
		});
	},

	getProvince: function () {
		$.ajax({
			url:' /basedata_api/Basedata_Project_Api/get_province_list/1/',
			type:'POST',
			data:{
			},
			dataType:'json',
			context: this,
			success:function(result){
				this.province_list = result.data.province_list;
                var str=""
                str +='<option value="">--省份--</option>'
                for(i=0;i<this.province_list.length;i++){
                    str += '<option value="' + this.province_list[i] + '">' + this.province_list[i] + '</option>';
                }
				$('#userProvince').html("").append(str);
			}
		});
	},

	getCity: function(province, city_select) {
		$.ajax({
			url:'/basedata_api/Basedata_Project_Api/get_city_obj_list_by_province/',
			async:false,
			type:'POST',
			data:{
				province:province,
			},
			dataType:'json',
			context: this,
			success:function(result){
				this.city_list = result.data.city_obj_list;
				city_select.html("").append($("<option value=''>--城市--</option>"));

                var temp = '<option value="<%=outer_city_id%>"><%=city%></option>';

                var co = _.template(temp);

                for(var i= 0; i < result.data.city_obj_list.length; i++){
                   var obj = {outer_city_id:this.city_list[i].outer_city_id, city:this.city_list[i].city};
                   city_select.append($(co(obj)));
                }

			}
		});
	},

	getProperty: function(property_name, property_select_ul){
		$.ajax({
			url:'/basedata_api/Basedata_Project_Api/get_property_list/',
			async:false,
			type:'POST',
			data:{
				property_name:property_name,
			},
			dataType:'json',
			context: this,
			success:function(result){
				var property_list = result.data.property_list;
				property_select_ul.html("");

                var temp = '<li data-value="<%=outer_id%>"><%=property%></li>';

                var co = _.template(temp);

                for(var i= 0; i < property_list.length; i++){
                    var obj = {outer_id:property_list[i].outer_property_id, property:property_list[i].property_name};
                   property_select_ul.append($(co(obj)));
                }

			}
		});
	},

	getProject: function  (province, city, project_select) {
		$.ajax({
			url:'/basedata_api/Basedata_Project_Api/get_project_list_by_filter/',
			async:false,
			type:'POST',
			data:{
			    province: province,
				city:city,
			},
			dataType:'json',
			context: this,
			success:function(result){

                var temp = '<option data-oid="<%=outer_project_id%>" value="<%=project%>"><%=project%></option>';

                var co = _.template(temp);
                var project_list = result.data.project_list;
                project_select.empty();

                for(var i= 0; i < project_list.length; i++){
                   var obj = {outer_project_id:project_list[i].outer_project_id, project:project_list[i].project};
                   project_select.append($(co(obj)));
                }

			}
		});
	},

    add_area:function(target_ul, name, area_id){
        var temp = '<li data-area_id=<%=area_id%>><span><%=name%></span> <i class="fa fa-remove"></i> </li>';
        var co = _.template(temp);
        var html = co({name:name, area_id:area_id});

        var exist_area_id_list = []
        target_ul.find("li").each(function(){
            exist_area_id_list.push($(this).data("area_id") + "");
        })

        if(area_id == ""){return}
        if(qd.utils.memberInList(area_id + "", exist_area_id_list)){return}
        $(target_ul).append($(html));
    },

    get_area_list:function(target_ul){
        var exist_area_id_list = []
        target_ul.find("li").each(function(){
            exist_area_id_list.push($(this).data("area_id") + "");
        })

        return exist_area_id_list;
    },

    bind_area:function(user_id, area_list){
        var self = this;


        $.ajax({
            url: '/user_api/Web_User_Api/bind_area/',
            type:'POST',
            data:{
                user_id:user_id,
                area: JSON.stringify(area_list),
            },
            dataType:'json',
            success:function(result){
                if(result.data.flag == 'Y'){
                    self.getUserList();
                }
            }
        })
    },

	events:{
	    'change .add-role':function(event){
	        var role = $('.add-role').val();
	        if(role == 2){
	            $('.add-web-user-username').removeClass('hide');
	            $('.add-web-user-phone').removeClass('hide');
	            $('.add-web-user-password').addClass('hide');
	        }else if(role == 3){
	            $('.add-web-user-username').addClass('hide');
	            $('.add-web-user-phone').removeClass('hide');
	            $('.add-web-user-password').removeClass('hide');

	        }else if(role == 4){
	            $('.add-web-user-username').removeClass('hide');
	            $('.add-web-user-phone').addClass('hide');
	            $('.add-web-user-password').removeClass('hide');
	        }
	    },

		'change .search-user-role':function(event){
			this.page_inited=false;
			this.getUserList();
		},

		'change .search-user-access':function(event){
			this.page_inited=false;
			this.getUserList();
		},
		
		'keyup .search-username':function(){
			var self = this;
			this.page_inited=false;
			window.clearTimeout(self.getUserListTimer);
			self.getUserListTimer = setTimeout(function(){self.getUserList();}, 400);
		},
		
		'keyup .search-phone':function(){
			var self = this;
			this.page_inited=false;
			window.clearTimeout(self.getUserListTimer);
			self.getUserListTimer = setTimeout(function(){self.getUserList();}, 400);
			
		},

		'keyup .edit_web_user_password': function () {
			password = $(".edit_web_user_password").val();
			if(password.length>6){UI.showErrTip("密码必须是6个字符")}
		},

		'click .add-web-user-btn':function(){
			var view=this;
			var username=$('.add-username').val();
			var phone=$('.add-phone').val();
			var role=$('.add-role').val();
			var access=$('.add-access').val();
			var password=$('.add-password').val();
			if(password) {
			    password = $.md5(password);
			}

			if(!role){
			    UI.showErrTip('请选择角色');
			    return false;
			}

			if(!access){
			    UI.showErrTip('请选择权限');
			    return false;
			}

			if(role == 2){
				if (!username) {
					UI.showErrTip('请填写用户名');
					return false;
				}
				if (!phone) {
					UI.showErrTip('请填写手机号');
					return false;
				}
				if (!/^1\d{10}$/gi.test(phone)) {
					UI.showErrTip('请填写正确的手机号码');
					return false;
				}
			}else if(role == 4) {
				if (!username) {
					UI.showErrTip('请填写用户名');
					return false;
				}
				if (!password) {
					UI.showErrTip('请填写密码');
					return false;
				}
			}else if(role == 3){
				if (!phone) {
					UI.showErrTip('请填写手机号');
					return false;
				}
				if (!/^1\d{10}$/gi.test(phone)) {
					UI.showErrTip('请填写正确的手机号码');
					return false;
				}
				if (!password) {
					UI.showErrTip('请填写密码');
					return false;
				}
			}

			
			$.ajax({
				url: '/user_api/Web_User_Api/add_web_user/',
				type: 'POST',
				data: {
					role: role,
					access: access,
					username: username,
					phone: phone,
					password:password
				},
				dataType: 'json',
				context: this,
				success:function(result){
					$('.add-web-user-btn').button('reset');
					if(result.data.flag != 'Y'){
						UI.showErrTip(result.msg);
						return false;
					}
                    UI.showSucTip('添加用户成功');
                    view.getUserList();
					$('.add-web-user').addClass('hide');
					$('.web-user-list-block').removeClass('hide');
				}
			});
		},
		
		'click .edit-web-user-btn':function(event){
			var _this = $(event.srcElement || event.target);
			var item=_this.parents("tr.web-user-item");
			var user_id=item.data("web-user-id");

			$('#edit-user-modal input[name="web_user_id"]').val(user_id);
			$('.modify-operation-type-select').change();
			$('#edit-user-modal').modal('show');
		},

		"change .modal-body select[name=province]":function(evt){
		    var self = this;
		    var province_select = $(evt.target);
		    var province_name = province_select.val();
            var city_select =  $(province_select).closest(".modal-body").find("select[name=city]");

		    self.getCity(province_name, city_select);
		},

		"change .modal-body select[name=city]":function(evt){
		    var self = this;
		    var city_select = $(evt.target);
		    var city_id = city_select.val();
		    var city_name = city_select.find("option:selected").text();

            var province_select =  $(city_select).closest(".modal-body").find("select[name=province]");
            var province_name = province_select.val();

            var project_select = $(city_select).closest(".modal-body").find("select[name=project]");
            if(project_select.size() > 0){
                self.getProject(province_name, city_name, project_select);
                return;
            }


            var area_ul = city_select.closest(".modal-body").find(".area_ul_list");

            self.add_area(area_ul, province_name + " - " + city_name, city_id);
		},

		"project_change .modal-body select[name=project]":function(evt){
            var self = this;
		    var project_select = $(evt.target);
		    var project_id = $(project_select).find("option:selected").data("oid");
		    var project_name = $(project_select).find("option:selected").text();

		    var area_ul = project_select.closest(".modal-body").find(".area_ul_list");
            self.add_area(area_ul, project_name, project_id);
		},

        "change .modal-body input.property[name=search_box_value]":function(evt){
            var self = this;
            var search_name = $(evt.target).val();
            var property_select_ul = $(evt.target).closest(".modal-body").find("ul.property_select_ul");
            self.getProperty(search_name,  property_select_ul);

        },

        "click ul.property_select_ul>li":function(evt){
            var self = this;
            var area_ul = $(evt.target).closest(".modal-body").find(".area_ul_list");
            var property_name = $(evt.target).text();
            var property_id = $(evt.target).data("value");
            self.add_area(area_ul, property_name, property_id);
        },

		"click a.access_btn": function(evt){
		    var self = this;
		    var access_val = $(evt.target).data("access");

		    var win = $("#user_access_type"+access_val+"_win");

		    pselect = win.find("div.modal-body select[name=province]");

            pselect.html("").append($("<option>--省份--</option>"));

            var temp = '<option value="<%=name%>"><%=name%></option>';

            co = _.template(temp);

		    for(var i= 0; i < this.province_list.length; i++){
		       pselect.append($(co({name:this.province_list[i]})))
		    }

		    var user_id = $(evt.target).closest("tr").data("web-user-id");

			self._select_user_id = user_id;

			$(evt.target).trigger("modal_win_open", {win:win,user_id:user_id});



		},

        "modal_win_open a.access_btn": function(evt, evt_data){
            var self = this;
		    var win = evt_data.win;
            var user_id = evt_data.user_id;

            var city_select = win.find("div.modal-body select[name=city]");
            var project_select = win.find("div.modal-body select[name=project]");
            var project_input = win.find("div.modal-body input[name=search_box_value]");

            city_select.html("").append($("<option>--城市--</option>"));
            project_select.html("");
            project_input.val("");


            $.ajax({
				url: '/user_api/Web_User_Api/get_area/',
				type: 'POST',
				data: {
					user_id: user_id,
				},
				dataType: 'json',
				context: this,
				success: function(result) {
					if (result.data.flag=="Y"){
					    var area_dict_list = result.data.area_dict_list;

					    var target_ul = win.find("ul.area_ul_list");
					    $.each(area_dict_list, function(i, item){
					        var area_id = item.area_id;
					        var name = item.area_str;
					        self.add_area(target_ul, name, area_id);
					    })
					}else{
						UI.showTips('danger',result.msg);
					}
				}
			})


        },

		"click .modal-footer button.bind_area_btn":function(evt){
		    var self = this;
		    var area_ul = $(evt.target).closest("div.modal").find("ul.area_ul_list");
		    var area_list = self.get_area_list(area_ul);
		    self.bind_area(self._select_user_id, area_list);

		    var win = $(evt.target).closest("div.modal");
		    win.modal("hide");
		},

		"click ul.area_ul_list>li i":function(evt){
		    var i_el = $(evt.target);
		    i_el.closest("li").remove();
		},

		'change .modify-operation-type-select':function(){
			$('#edit-user-modal input[name="web_user_username"]').val('');
			$('#edit-user-modal input[name="web_user_password"]').val('');
			$('#edit-user-modal input[name="web_user_phone"]').val('');
			$('.user-forbidden').val('');
			var operation_type=$('.modify-operation-type-select').val();
			var access = $('#edit-user-modal input[name="web_user_access"]').val();
			if(operation_type==1){
				$('.modify-username-tr').removeClass('hide');
				$('.modify-phone-tr').addClass('hide');
				$('.reset-password-tr').addClass('hide');
				$('.user-forbidden-tr').addClass('hide');
			}else if(operation_type==2){
				$('.modify-phone-tr').addClass('hide');
				$('.modify-username-tr').addClass('hide');
				$('.reset-password-tr').removeClass('hide');
				$('.user-forbidden-tr').addClass('hide');
			}else if(operation_type==3){
				$('.modify-phone-tr').addClass('hide');
				$('.modify-username-tr').addClass('hide');
				$('.reset-password-tr').addClass('hide');
				$('.user-forbidden-tr').removeClass('hide');
			}else if(operation_type==4){
				$('.modify-phone-tr').removeClass('hide');
				$('.modify-username-tr').addClass('hide');
				$('.reset-password-tr').addClass('hide');
				$('.user-forbidden-tr').addClass('hide');
			}
		},

		'click .submit-web-user-btn':function(){
			var user_operation_type=$('.modify-operation-type-select').val();
			var user_id = $('#edit-user-modal input[name="web_user_id"]').val();
			var phone = $('#edit-user-modal input[name="web_user_phone"]').val();
			var password = $('#edit-user-modal input[name="web_user_password"]').val();

			if (user_operation_type=='4' && !/^1\d{10}$/gi.test(phone)) {
				UI.showErrTip('请填写正确的手机号码');
				return false;
			}
			

            var url = '/user_api/Web_User_Api/modify_user/';
            if (password) {
                if(password.length>6){
                    UI.showErrTip("密码必须是6个字符");
                    return false;
                }
                password = $.md5(password);
            }
            var data = {
                user_id: user_id,
                username: $('#edit-user-modal input[name="web_user_username"]').val(),
                password: password,
                status: $('.user-forbidden').val(),
                phone:phone,
            }

			
			$.ajax({
				url: url,
				type: 'POST',
				data: data,
				dataType: 'json',
				context: this,
				traditional: true,
				success:function(result){
                    if (result.data.flag != "Y") {
                        UI.showErrTip(result.msg);
                        return false;
                    }
                    UI.showSucTip('修改成功');
                    $('#edit-user-modal').modal('hide');
                    this.getUserList();
                }					
			});
		},
		
		'click .search-user-btn':function(){
			var view=this;
			window.clearTimeout(view.getUserListTimer);
			view.getUserListTimer = setTimeout(function(){view.getUserList();},400);
		},
		
		'click .remove-web-user-btn':function(event){
			if (!confirm('确定要删除吗？')) return true;
			var item=$(event.srcElement || event.target).parents("tr.web-user-item");
			var self = this;
			 
			$.ajax({
				url:'/user_api/Web_User_Api/remove_web_user/1/',
				type:'POST',
				data:{
					user_id:item.data('web-user-id'),
				},
				dataType:'json',
				success:function(result){
					if(result.data.flag!='Y'){
						$('.notifications').notify({
							type:'dange',fadeOut:{enabled:true,delay:3000},
							message:{text:result.msg}
						}).show();
						return false;
					}
					
					self.getUserList();
					$('.notifications').notify({
						type:'info',fadeOut:{enabled:true,delay:1000},
						message:{text:'删除成功'}
					}).show();
				}
			});
		},

        'click .project_select_input':function(evt){
            var ops = $(evt.target).siblings("select").find("option");
            var ul = $(evt.target).siblings("ul");
            ul.empty();
            var value = $(evt.target).val();
            $(ops).each(function(){
                if ($(this).val().indexOf(value) != -1) {
                    ul.append("<li>"+$(this).val()+"</li>");
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
            if($(evt.target).is(".project_select_input")){return}
            if($(evt.target).closest("ul.project_select_ul").size() == 0){
                $("ul.project_select_ul").hide();
            }
        },

        'click .project_select_ul>li':function(evt){
            var project = $(evt.target).text();

            $(evt.target).parent("ul").siblings("input").val(project);
            var project_select = $(evt.target).parent("ul").siblings("select[name=project]");
            project_select.val(project);
            project_select.trigger("project_change", {});

            $(evt.target).parent("ul").html("").hide();
        },

	},



});
