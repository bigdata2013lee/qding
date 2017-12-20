var brake_device_monitoring_view = Backbone.View.extend({
    template: versionify(CONST.static_url + 'community/ejs/device_monitoring_block.html'),
    page_no: 1,
    page_size: 30,
    page_inited: false,
    addIndex: 1,
    get_brake_list_timer: null,

    initialize: function () {
        $(this.el).html(new EJS({url: this.template}).render({}));
        var view = this;

        view.sort_direction = '-';
        view.sort_field = 'position';
        setTimeout(function () {
            view.loadData();
        }, 10 * 1);
    },

    loadData: function () {
        this.getList();
        this.getGroupList();
        this.getBuildList();
    },

    setMonitoring:function(device_id, is_monit) {
        $.ajax({
            url: '/brake_api/Brake_Machine_Api/set_brake_monit/',
            type: 'POST',
            data: {
                brake_id: device_id,
                is_monit: is_monit,
            },
            dataType: 'json',
            success: function(result) {
                if(result.data.flag == 'N'){UI.showErrTip(result.msg);}
            }
        });
    },

    getGroupList: function () {
        $('.search-brake-group').html('<option value="">--  组团  --</option>');
        $('.search-brake-group').val("");
        $.ajax({
            url: '/basedata_api/Basedata_Group_Api/get_group_list/1/',
            type: 'POST',
            data: {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
            },
            dataType: 'json',
            success: function (result) {
                var group_list = result.data.group_list;
                UI.createSimpleOption($('.search-brake-group'), group_list);
                $('.search-brake-group').change();
            }
        });
    },

    getBuildList: function () {
        var self = this;
        if(self.group_list && !!!$('.pass-data-group').val()){return false;}
        $.ajax({
            url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
            type: 'POST',
            data: {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $('.search-brake-group').val(),
            },
            dataType: 'json',
            success: function (result) {
                UI.createSimpleOption($(".pass-data-build"),result.data.build_list);
            }
        });
    },

    getList: function (pageIndex, order_filed) {
        if (typeof pageIndex == "undefined") {
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;
        $.ajax({
            url: '/brake_api/Brake_Machine_Api/get_brake_status/1/',
            type: 'POST',
            data: {
                page_no: _this.page_no,
                page_size: _this.page_size,
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $('.search-brake-group').val(),
                build: $('.search-brake-build').val(),
                unit: $('.search-brake-unit').val(),
                brake_type: $('.search-brake-type').val(),
                lately_pass: $('.search-brake-pass').val(),
                status: $('.search-brake-status').val(),
                mac: $('.search-brake-mac').val(),
                order_filed: order_filed,
            },
            dataType: 'json',
            success: function (result) {
                if (result.data.flag == "Y") {
                    var user_type = $("#userType").text();
                    var ejs_html = new EJS({url: CONST.static_url + 'community/ejs/device_monitoring_list_block.html?' + Math.random()})
                        .render({list: result.data.brake_list, sort_direction: _this.sort_direction,
                        sort_field: _this.sort_field, user_type: user_type});
                    $(_this.el).find('.list-block').html(ejs_html);
                    if (!_this.page_inited) {
                        _this.initPager(result.data.pagination.total_count);
                    }
                    $("#onlineNum").html(result.data.online_num);
                    $("#offlineNum").html(result.data.offline_num);
                    $('input[name="switch"]').bootstrapSwitch();
                    var str = '<button type="button" class="btn btn-info">总数：' + result.data.pagination.total_count + '</button>';
                    $(".brake_count").html(str);
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
                    _this.getList(_this.page_no, "updated_time");
                }
            },
            items_per_page: _this.page_size, //每页显示1项
            prev_text: "«",
            next_text: "»"
        });
        this.page_inited = true;
    },


    events: {
        // 添加邮件接收人
        'click .edit-add-email-btn': function () {
            $("#alert_email_list").append(this.createEmail(email = ""));
            this.addIndex++;
        },
        // 删除邮件接收人
        'click .edit-del-email-btn': function (event) {
            $(event.srcElement || event.target).parent().remove();
        },

        'click .edit-item-btn': function (event) {
            var item = $(event.srcElement || event.target).parents('tr');
            var heart_time = item.data("heart-time");
            if (heart_time === 0) {
                $('#heart_time').val("");
            } else {
                $('#heart_time').val(heart_time);
            }
            $('#edit_modal').modal('show');
            $('input[name="edit_item_id"]').val(item.data("device-id"));
        },

        'click .bootstrap-switch': function (event) {
            var item = $(event.srcElement || event.target).parents('.bootstrap-switch');
            var tr = item.parents('tr');
            var edit = tr.find(".operate-edit");
            var cls = item.attr("class").indexOf("switch-on");
            if (cls > 0) {
                edit.addClass("edit-item-btn");
                this.setMonitoring(tr.data("device-id"), 1);
            } else {
                edit.removeClass("edit-item-btn");
                this.setMonitoring(tr.data("device-id"), 0);
            }
        },

        'click .operate-edit':function (event){
            var tr = $(event.target).closest("tr");
            var id = tr.data('device-id');
            $('input[name=edit_item_id]').val(id);
            $('#edit_modal').modal('show');
        },

        'click .edit-submit-btn': function () {
            var id = $('input[name=edit_item_id]').val();
            var val = $('#heart_time').val();
            var reg = /^\d{1,4}(\.\d{1,2})?$/;
            if (!reg.test(val)) {
                UI.showErrTip("请输入整数部位不超过4位，小数部位不超过2位的正有理数");
                return true;
            }
            $.ajax({
                url: '/brake_api/Brake_Machine_Api/set_brake_heart_time/1/',
                type: 'POST',
                data: {
                    brake_id: id,
                    heart_time: val
                },
                context: this,
                dataType: 'json',
                success: function () {
                    $('#edit_modal').modal('hide');
                    this.getList(false, "updated_time");
                }
            });
        },

        'click .brake_dump':function(){
            var data  = {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $('.search-brake-group').val(),
                build: $('.search-brake-build').val(),
                unit: $('.search-brake-unit').val(),
                brake_type: $('.search-brake-type').val(),
                lately_pass: $('.search-brake-pass').val()
            };
            var get_str = $.param(data);
            $.ajax({
                url: '/brake_api/Brake_Machine_Api/dump_brake_machine/',
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function(result){
                    if(result.data.flag == 'N') {
                        UI.showErrTip("正在准备数据，请稍候");
                    }else{
                        var url = '/dump_brake_machine_to_excel?' + get_str;
                        window.location.href = url;
                    }
                }
            });
        },

        'change .search-brake-group': function () {
            $('.search-brake-build').html('<option value="">--  楼栋  --</option>');
            $('.search-brake-build').val("");
            $('.search-brake-build').change();
            $.ajax({
                url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
                type: 'POST',
                data: {
                    province: $("#sProvince").html(),
                    city: $("#sCity").html(),
                    project: $("#sCommunity").html(),
                    group: $('.search-brake-group').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var build_list = result.data.build_list;
                    UI.createSimpleOption($('.search-brake-build'), build_list);
                }
            });
        },

        'change .search-brake-build': function () {
            $('.search-brake-unit').html('<option value="">--  单元  --</option>');
            $('.search-brake-unit').val("");
            $('.search-brake-unit').change();
            var build = $('.search-brake-build').val();
            if (!build) {
                return false;
            }
            $.ajax({
                url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
                type: 'POST',
                data: {
                    province: $("#sProvince").html(),
                    city: $("#sCity").html(),
                    project: $("#sCommunity").html(),
                    group: $('.search-brake-group').val(),
                    build: $('.search-brake-build').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var unit_list = result.data.unit_list;
                    UI.createSimpleOption($('.search-brake-unit'), unit_list);
                }
            });
        },

        'change .search-brake-unit': function () {
            this.page_inited = false;
            this.getList(false, "updated_time");
        },

        'change .search-brake-type': function() {
            this.page_inited = false;
            this.getList(false, "updated_time");
        },

        'change .search-brake-pass':function() {
            this.page_inited = false;
            this.getList(false, "updated_time");
        },

        'change .search-brake-status': function() {
            this.page_inited = false;
            this.getList(false, "updated_time");
        },

        'click .remove-brake-btn': function (event) {
            var item = $(event.srcElement || event.target).parents('tr.brake-item');
            var status = item.data("device-status");
            var msg_str = '';
            if (status=="1"){
                if (!confirm('确定要删除吗？')) return true;
                var url = '/brake_api/Brake_Machine_Api/delete_brake/1/';
                msg_str = '删除成功';
            }else if(status=="2"){
                if (!confirm('确定要恢复吗？')) return true;
                var url = '/brake_api/Brake_Machine_Api/resume_brake/1/';
                msg_str = '恢复成功';
            }


            $.ajax({
                url: url,
                type: 'POST',
                context: this,
                data: {
                    brake_id: item.data('device-id')
                },
                dataType: 'json',
                success: function (result) {
                    item.remove();
                    UI.showTips('info', msg_str);
                }
            });
        },

        'keyup .search-brake-mac': function() {
            var self = this;
            self.page_no = 1;
            self.page_inited = 'undefined';
            window.clearTimeout(self.get_brake_list_timer);
            var sort_value = self.sort_direction + self.sort_field;
            self.get_brake_list_timer = setTimeout(function(){self.getList(false, "updated_time")}, 400);
        },

        'click th.sortable':function(evt){
            var field = $(evt.currentTarget).closest('th').data('field');
            var direction = $(evt.currentTarget).closest('th').data('direction');
            if(direction=='-'){
                direction = ''
            }else{
                direction= '-'
            }

            this.sort_field = field;
            this.sort_direction = direction;

            this.getList(false, direction + field);
        },
    }
});

