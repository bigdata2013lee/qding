var brake_qr_pass_data_view = Backbone.View.extend({
    className: 'brake_qr_pass_data_view',
    template: versionify(CONST.static_url + 'community/ejs/brake_qr_pass_data_block.html'),
    user_type: '',
    page_no: 1,
    page_size: 30,
    page_inited: false,
    group_list:null,

    initialize: function () {
        $(this.el).html(new EJS({url: this.template}).render({}));
        var view = this;
        view.loadData();
        view.checkUserType();
        $(this.el).find('.dump-excel-date').datetimepicker({
            language: 'zh-CN',
            todayBtn: 1,
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
    },

    checkUserType: function () {
        var type = $("#userType").html();
        if (type === "2") {
            $("#userType").addClass("hidden");
            $(".bindPhoneInfo").addClass("hidden");
        }
    },

    loadData: function () {
        this.getGroupList();
        this.getBuildList();
        this.getList();
    },

    getList: function (pageIndex) {
        if (typeof pageIndex == "undefined") {
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;

        var data_flag = $("input:radio[name='data_flag']:checked").val();
        var post_url = '/brake_api/Brake_Pass_Api/get_try_pass_list_by_position/1/';
        if(data_flag=="1"){
            post_url = '/brake_api/Brake_Pass_Api/get_pass_list_by_position/1/';
        }

        $.ajax({
            url: post_url,
            type: 'POST',
            data: {
                pass_type: $('.pass-data-type').val(),
                page_no: _this.page_no,
                page_size: _this.page_size,
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $(".pass-data-group").val(),
                build: $(".pass-data-build").val(),
                unit: $(".pass-data-unit").val(),
                brake_type: $(".pass-data-brake-level").val(),
            },
            dataType: 'json',
            success: function (result) {
                if (result.data.flag=='Y'){
                    var ejs_html = new EJS({url: CONST.static_url + 'community/ejs/qr_pass_data_list_block.html?' + Math.random()})
                        .render({pass_list: result.data.pass_list});
                    $(_this.el).find('.qr-pass-data-list-block').html(ejs_html);
                    if (result.data.pagination) {
                        if (!_this.page_inited) {
                            _this.initPager(result.data.pagination.total_count);
                        }
                    }
                }
            }
        });
    },

    // 分页
    initPager: function (total) {
        var _this = this;
        $('#pagination').pagination(total, {
            num_edge_entries: 1, //边缘页数
            num_display_entries: 4, //主体页数
            callback: function (pageIndex, jq) {
                if (_this.page_inited) {
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


    _get_area_info: function () {
        return {
            province: $("#sProvince").html(),
            city: $("#sCity").html(),
            project: $("#sCommunity").html()
        }
    },

    getGroupList: function () {
        var self = this;
        $(".pass-data-group").empty();
        $(".pass-data-group").append("<option value=''>组团</option>");
        self.group_list = null;
        $.ajax({
            url: '/basedata_api/Basedata_Group_Api/get_group_list/1/',
            type: 'POST',
            data: $.extend({}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                UI.createSimpleOption($(".pass-data-group"),result.data.group_list);
                self.group_list = result.data.group_list;
            }
        });
    },

    getBuildList: function () {
        var self = this;
        $(".pass-data-build").empty();
        $(".pass-data-build").append("<option value=''>楼栋</option>");
        $.ajax({
            url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
            type: 'POST',
            data: $.extend({group: $(".pass-data-group").val()}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                UI.createSimpleOption($(".pass-data-build"),result.data.build_list);
            }
        });
    },

    getUnitList:function(){
        var self = this;
        if(!!!$(".pass-data-build").val()){return false;}
        $.ajax({
            url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
            type: 'POST',
            data: $.extend({group: $(".pass-data-group").val(), build: $(".pass-data-build").val()}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                UI.createSimpleOption($(".pass-data-unit"),result.data.unit_list);
            }
        });
    },


    events: {
        'change .pass-data-group': function(){
            $(".pass-data-build").empty();
            $(".pass-data-build").append("<option value=''>楼栋</option>");
            this.getBuildList();
            $(".pass-data-build").change();
        },

        'change .pass-data-build': function(){
            $(".pass-data-unit").empty();
            $(".pass-data-unit").append("<option value=''>单元</option>");
            this.getUnitList();
            $(".pass-data-unit").change();
        },

        'change .pass-data-unit':function(){
            this.getList();
        },

        'change .pass-data-brake-level':function() {
            this.getList();
        },

        'change .pass-data-type': function () {
            this.getList();
        },

        'change input:radio[name="data_flag"]': function(){
            var data_flag = $("input:radio[name='data_flag']:checked").val();
            var pass_data_type = $(".pass-data-type");
            if(data_flag=="1"){
                $(".pass-data-type option[value='6']").remove();
                $(".pass-data-type option[value='11']").remove();
            }else{
                if(pass_data_type.size()<7){
                    pass_data_type.append('<option value="6">拆除</option>');
                    pass_data_type.append('<option value="11">调试</option>');
                }
            }
            this.getList();
        },

        'click .brake-dump-excel-btn': function () {
            $("#dump_data_modal span.dump_data_type").text('brake_pass');
            $('#dump_data_modal').modal('show');
        },

        'click .submit-dump-excel-btn': function (event) {
            var start_time = new Date($('.start-time').val()).getTime() / 1000;
            var end_time = new Date($('.end-time').val()).getTime() / 1000;

            if (!!!start_time || !!!end_time) {
                UI.showErrTip('请填写完整信息');
                return false;
            }

            if(start_time*1 >= end_time*1){
                UI.showErrTip("结束时间必须比开始时间晚");
                return false;
            }


            var modal = $(event.srcElement || event.target).parents('#dump-data-option');
            var data = {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                start_time: new Date($('.start-time').val()).getTime() / 1000,
                end_time: new Date($('.end-time').val()).getTime() / 1000
            };

            var get_str = $.param(data);
            var url = '/dump_pass_list_to_excel?' + get_str;
            modal.modal('hide');
            window.location.href = url;
        }
    }
});

