
(function($) {

    var mm = qd.ns("views.project");
    mm.ProjectView = Backbone.View.extend({
        className: 'view_box',
        _tpl:'/static/qd/projects/tpls/projects.tpl',
        cityUrl: "pcity.PCityApi.list_pcitys",
        allCitiesUrl: "pcity.PCityApi.list_all_pcitys",
        token: true,
        _query_pager:{},
        pid:'',
        events: {
            "click button.query_btn":function (evt) {
                this.query_project_list();
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                this._query_pager.page_no =  page_no == 0 || isNaN(page_no) ? 1 : page_no;
                this.query_project_list();
            },
            'click button.add_project': function (evt) {
                this.$el.find("#projects_form").qd_province_city_select( this.allCitiesUrl );
            },
            'click .sumbit_btn_add_project': function (evt) {
                 this.submit_projects_data();
            },
            'click a.aptm_modal': function (evt) {
                $(".import input[name=project_id]").val($(evt.target).closest("tr").data('oid'));
            },
            'click a.modify_info': function (evt) {
                var oTr = $(evt.target).closest("tr");
                $(".modify_project input[name=project_id]").val(oTr.data('oid'));
                $(".modify_project input[name=project_code]").val(oTr.data('code'));
                $(".modify_project input[name=name]").val(oTr.data('name'));
                $(".modify_project input[name=label]").val(oTr.data('label'));
                $(".modify_project input[name=street]").val(oTr.data('street'));
            },
            'click div.import button.sumbit_btn': function (evt) {
                this.submit();
            },
            'click .remove_project': function (evt) {
                this.submit_remvoe_project( $(evt.target).closest("tr").data('oid') );
            },
            'click .reset_passwd': function (evt) {
                this.submit_reset_passwd( $(evt.target).closest("tr").data('oid') );
            },
            'click div.modify_project button.sumbit_btn': function (evt) {
                this.submit_modify_info();
            },
            'click .modifylist':function(evt){
            	var self = this;
            	self.pid = $(evt.target).closest("tr").data('oid')
            	$(".projectcode").val($(evt.target).closest("tr").data('code'))
            },
            'click .add_project_panel .close': function (evt) {
                $("pre").hide();
                $('#projects_form').get(0).reset();
                $('#add_project_window').modal('hide');
            }
        },

        initialize: function () {
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html( this.el );
            this.$el.find(".query_box>form").qd_province_city_select( this.cityUrl );
            this.query_project_list();
        },

        query_project_list: function () {
            var self = this, params = qd.utils.serialize('div.query_box');
            qd.rpc("projectmgr.ProjectMgrApi.list_projects", $.extend({pager: self._query_pager}, params)).success(function (result) {
                self.$el.find(".data_list_box").render_template( result );
            });
        },

        _v:function (params) {
            var rules={
                "pcity_id": "required",
                "ccity_id": "required",
                "street": {method: "regex", exp: /^([\u4E00-\u9FA5]|\w|-){1,100}$/},
                //"project_code": {"method":"regex", exp:/^[0-9]{6}$/},
                "project_name": {method: "regex", exp: /^([\u4E00-\u9FA5]|\w|-){1,100}$/},
                "label": {method: "regex", exp: /^([\u4E00-\u9FA5]|\w|-){1,100}$/},
                //,"wy_username": "required"
            };
            var messages={
                //"project_code": "请输入6位数字项目编码",
                "project_name": "请输入有效社区名称",
                "street": "请输入有效街道信息",
                "label": "请输入有效标签信息",
                "pcity_id": "请选择省份",
                "ccity_id": "请选择城市"
                //,"wy_username": "请输入管理员帐号"
            };
            var v = new qd.utils.Validator(rules, messages);
            return v.validate(params);
        },

        submit_modify_info: function ( pid ) {
            var self = this,params = qd.utils.serialize('div.modify_project');
            params.project_id = self.pid;
            delete params.project_code;
            qd.rpc("projectmgr.ProjectMgrApi.set_project_infos", params).success(function (result) {
                $('#modify_info_window').modal('hide');
                if(result.err == 0){
                    setTimeout(function () {
                        self.query_project_list();
                    }, 200);
                }
            });
        },

        submit_reset_passwd: function ( pid ) {
        	if(!window.confirm("是否重置密码？")) { return; }
            qd.rpc("projectmgr.ProjectMgrApi.reset_wy_password", { project_id :  pid }).success(function (result) {
                Object.keys(  result.data ).forEach(function(key,index){
                    $("#"+ key).html( result.data[key] )
                })
                $("#init_pwd").html(result.data.project_code+'/'+result.data.init_pwd)
            });
            $("#reset_passwd_window").modal('show');
        },

        submit_remvoe_project: function ( pid ) {
        	if(!window.confirm("是否要删除该社区？")) { return; }
            var self = this;
            qd.rpc("projectmgr.ProjectMgrApi.remove_project", { project_id :  pid }).success(function (result) {
                self.query_project_list();
            });
        },

        submit_projects_data: function () {
            var self = this, params = qd.utils.serialize('div.add_project'), params1 = params;
            if(!this._v(params)) return;
            delete params.pcity_id;
            qd.rpc("projectmgr.ProjectMgrApi.add_project", params).success(function (result) {
                self.query_project_list();
                if(result.err == 0){
                	 result.Province = $(".Province").find("option:selected").text(); 
                	 result.City = $(".City").find("option:selected").text();
                	 result.street = params.street;
                	 result.project_name = params.project_name;
                    self.$el.find(".data_msg_box").render_template(result);
                }
                 $('#Administrators').modal('show');
                $('#add_project_window').modal('hide');
                $('#projects_form').get(0).reset();
            });
        },
        _validate1:function(params){
            var self = this, _rs = true, definition = self.$el.find('#import_aptm_window_form input[name=csv_file]').val();
            if(definition == ''){
                _rs=false;
                qd.notify.error('请选择上传的定义文件');
            }
            return  _rs;
        },
        submit:function(){
            var self = this,params = qd.utils.serialize(self.$el.find('#import_aptm_window_form'));
            if(!self._validate1(params)){return;}
            if(!window.confirm('提交前，请仔细核对信息。\n\n你确认要导入此文件？')){return;}

            if(self.token){
                self.token = false;
                var oProgress = $('.progress').show();
                $('#import_aptm_window_form').ajaxSubmit({
                    url: '/remote/aptm.AptmImportExportApi.import_csv/',
                    type: 'POST',
                    dataType: 'json',
                    beforeSubmit: function(form_data, jq_form, options) {
                        form_data.push({name:"_params", value:JSON.stringify(params)});
                    },
                    uploadProgress: function(event, position, total, percent){
                        $('#percent').css('width', ' ' + percent + '%').children("span").html(' ' + percent + '%');
                    },
                    success: function(result) {
                        if(result.err > 0){
                            qd.notify.error(result.msg);
                            $("#errorInfo").html(result.msg).show();
                        }else{
                            qd.notify.info(result.msg);
                            $("#errorInfo").html("").hide();
                            $('#import_aptm_window_form')[0].reset();
                            $('#import_aptm_window').modal('hide');
                        }
                    },
                    complete: function(xhr, ts) {
                        oProgress.hide();
                        $('#percent').css('width', '0');
                        self.token = true;
                    }
                });
            }
        }

    });

})(jQuery);