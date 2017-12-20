var brake_machine_manage_view = Backbone.View.extend({
    className: 'brake-machine-manage-view',
    template: versionify(CONST.static_url + 'manage/ejs/brake_machine_manage_block.html'),

    page_no: 1,
    page_size: 30,
    page_inited: false,
    get_brake_list_timer: 0,


    initialize: function () {
        $(this.el).html(new EJS({url: this.template}).render({}));
        this.page_no = 1;
        this.page_size = 30;
        this.get_brake_list(this.page_no, "created_time");
        this.sort_field = 'position.province';
        this.sort_direction = '-';
    },

    initPager: function (total) {
        var _this = this;
        _this.page_inited = false;
        $('#pagination').pagination(total, {
            num_edge_entries: 1, //边缘页数
            num_display_entries: 4, //主体页数
            callback: function (pageIndex, jq) {
                _this.page_no = pageIndex + 1;
                if(_this.page_inited){
                    _this.get_brake_list(_this.page_no, _this.sort_direction+_this.sort_field);
                }
            },
            items_per_page: _this.page_size, //每页显示1项
            prev_text: "«",
            next_text: "»"
        });
        this.page_inited = true;
    },

    get_brake_list: function (pageIndex, order_field) {
        var _this = this;
        $.ajax({
            url: '/brake_api/Brake_Machine_Api/get_brake_machine_by_filter/1/',
            type: 'POST',
            data: {
                province: $(_this.el).find('.search-brake-province').val(),
                city: $(_this.el).find('.search-brake-city').val(),
                project: $(_this.el).find('.project_select_input').val(),
                group: $(_this.el).find('.search-brake-group').val(),
                build: $(_this.el).find('.search-brake-build').val(),
                unit: $(_this.el).find('.search-brake-unit').val(),
                mac: $(_this.el).find('.search-brake-mac').val(),
                firmware_version: $(_this.el).find('.search-brake-firmware').val(),
                hardware_version: $(_this.el).find('.search-brake-hardware').val(),
                lately_pass: $(_this.el).find('.search-brake-pass').val(),
                page_no: pageIndex,
                page_size: _this.page_size,
                order_field: order_field,
            },
            dataType: 'json',
            success: function (result) {
                var ejs_html = new EJS({url: CONST.static_url + 'manage/ejs/brake_list_block.html?' + Math.random()})
                    .render({brake_machine_list: result.data.brake_machine_list,sort_direction: _this.sort_direction, sort_field: _this.sort_field});
                $(_this.el).find('.brake-list-block').html(ejs_html);
                var str = '<button type="button" class="btn btn-info">总数：' + result.data.pagination.total_count + '</button>';
                $(".brake_machine_count").html(str);
                if (result.data.pagination && result.data.brake_machine_list.length > 0) {
                    if(_this.page_inited == 'undefined'){
                        _this.initPager(result.data.pagination.total_count);
                    }
                } else {
                    $('#pagination').html('');
                }
            }
        });
    },

    get_build_list: function () {
        var _this = this;
        $.ajax({
            url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
            type: 'POST',
            data: {
                province: $(_this.el).find('.add-brake-province').val(),
                city: $(_this.el).find('.add-brake-city').val(),
                project: $(_this.el).find('.add-brake-project').val(),
                group: $(_this.el).find('.add-brake-group').val(),
            },
            dataType: 'json',
            success: function (result) {
                var build_list = result.data.build_list;
                var str = '';
                for (var i = 0; i < build_list.length; i++) {
                    str += '<option value="' + build_list[i] + '">' + build_list[i] + '</option>';
                }
                $(_this.el).find('.add-brake-build').append(str);
            }
        });
    },

    get_unit_list: function () {
        var _this = this;
        $.ajax({
            url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
            type: 'POST',
            data: {
                province: $(_this.el).find('.add-brake-province').val(),
                city: $(_this.el).find('.add-brake-city').val(),
                project: $(_this.el).find('.add-brake-project').val(),
                group: $(_this.el).find('.add-brake-group').val(),
                build: $(_this.el).find('.add-brake-build').val(),
            },
            dataType: 'json',
            success: function (result) {
                var unit_list = result.data.unit_list;
                var str = '';
                for (var i = 0; i < unit_list.length; i++) {
                    str += '<option value="' + unit_list[i] + '">' + unit_list[i] + '</option>';
                }
                $(_this.el).find('.add-brake-unit').append(str);
            }
        });
    },

    get_list: function(pageIndex, order_field) {
        this.get_brake_list(pageIndex, order_field);
    },

    /**
     * 创建下拉框选项
     * @param  {object} data    循环创建的列表对象
     * @param  {string} prop    选中项的值
     * @param  {string} target  需要创建选项的下拉框
     * @param  {string} unitStr 给列表值添加单位
     * @param  {boolean} bool   设置value值是否为数字或列表值
     */
    createOption: function (data, prop, target, unitStr, bool) {
        var str = '', val = '';
        for (var i = 0; i < data.length; i++) {
            val = bool ? i : data[i];
            if (unitStr) {
                if (data[i].indexOf(unitStr) === -1) {
                    data[i] += unitStr;
                }
            }
            str += '<option value="' + val + '"';
            if (val == prop) {
                str += " selected";
            }
            str += '>' + data[i] + '</option>';
        }
        $('#edit_brake_modal ' + target).append(str);
    },

    createOptionTwo: function (data, prop, target) {
        this.createOption(data, prop, target, null, true);
    },

    createGateOption: function (data, prop, target) {
        var str = '', val = '';
        for (var i = 0; i < data.length; i++) {
            val = data[i].gate_id;
            str += '<option value="' + val + '"';
            if (val == prop) {
                str += " selected";
            }
            str += '>' + data[i].position + '</option>';
        }
        $('#edit_brake_modal ' + target).append(str);
    },
    // 检查输入格式
    checkBrakeInput: function (obj, type, msg, bool) {
        var reg_type = bool ? (/^\d+$/) : /^-\d+$/;
        var val = obj.find('input[name="' + type + '"]').val();
        if (val !== '' && !reg_type.test(val)) {
            UI.showTips('danger', msg);
            return false;
        }
        return true;
    },
    //判断mac地址的正则
    reg_mac: /^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){5}$/,
    reg_mac_two: /^[0-9a-fA-F]{2}([0-9a-fA-F]{2}){5}$/,
    events: {
        'change .search-brake-city': function () {
            $('.search-brake-project').html('--楼盘--');
            $('.search-brake-project').val('');
            $('.project_select_input').val('');
            $('.search-brake-project').change();

            if (!$('.search-brake-city').val()) {
                return true;
            }

            $.ajax({
                url: '/basedata_api/Basedata_Project_Api/get_project_list_by_city/1/',
                type: 'POST',
                data: {
                    province: $('.search-brake-province').val(),
                    city: $('.search-brake-city').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var project_list = result.data.project_list;
                    UI.createSimpleOption($('.search-brake-project'), project_list);
                }
            });
        },

        'change .search-brake-project': function () {
            $('.search-brake-group').html('<option value="">-- 组团 --</option>');
            $('.search-brake-group').val('');
            $('.search-brake-group').change();

            if (!$('.project_select_input').val()) {
                return true;
            }

            $.ajax({
                url: '/basedata_api/Basedata_Group_Api/get_group_list/1/',
                type: 'POST',
                data: {
                    province: $('.search-brake-province').val(),
                    city: $('.search-brake-city').val(),
                    project: $('.project_select_input').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var group_list = result.data.group_list;
                    UI.createSimpleOption($('.search-brake-group'), group_list);
                }
            });
        },

        'change .search-brake-group': function () {
            $('.search-brake-build').html('<option value="">--楼栋--</option>');
            $('.search-brake-build').val('');
            $('.search-brake-build').change();

            if (!$('.search-brake-project').val()) {
                return true;
            }

            $.ajax({
                url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
                type: 'POST',
                data: {
                    'province': $('.search-brake-province').val(),
                    'city': $('.search-brake-city').val(),
                    'project': $('.project_select_input').val(),
                    'group': $('.search-brake-group').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var build_list = result.data.build_list;
                    UI.createSimpleOption($('.search-brake-build'), build_list);
                }
            });
        },

        'change .search-brake-build': function () {
            $('.search-brake-unit').html('<option value="">--单元--</option>');
            $('.search-brake-unit').val('');
            $('.search-brake-unit').change();

            if (!$('.search-brake-build').val()) {
                return true;
            }

            $.ajax({
                url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
                type: 'POST',
                data: {
                    'province': $('.search-brake-province').val(),
                    'city': $('.search-brake-city').val(),
                    'project': $('.project_select_input').val(),
                    'group': $('.search-brake-group').val(),
                    'build': $('.search-brake-build').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var unit_list = result.data.unit_list;
                    UI.createSimpleOption($('.search-brake-unit'), unit_list);
                }
            });
        },

        'change .search-brake-unit': function () {
            this.page_no = 1;
            this.page_inited = 'undefined';
            this.get_list(this.page_no, this.sort_direction+this.sort_field);
            $('.add-brake').addClass('hide');
        },

        'change .search-brake-pass': function() {
            this.page_no = 1;
            this.page_inited = 'undefined';
            this.get_brake_list(this.page_no, this.sort_direction+this.sort_field);
        },

        'keyup .search-brake-firmware': function() {
            var self = this;
            self.page_no = 1;
            self.page_inited = 'undefined';
            window.clearTimeout(self.get_brake_list_timer);
            var sort_value = self.sort_direction + self.sort_field;
            self.get_brake_list_timer = setTimeout(function(){self.get_brake_list(self.page_no, sort_value)}, 400);
        },

        'keyup .search-brake-hardware': function() {
            var self = this;
            self.page_no = 1;
            self.page_inited = 'undefined';
            window.clearTimeout(self.get_brake_list_timer);
            var sort_value = self.sort_direction + self.sort_field;
            self.get_brake_list_timer = setTimeout(function(){self.get_brake_list(self.page_no, sort_value)}, 400);
        },

        'keyup .search-brake-mac': function() {
            var self = this;
            self.page_no = 1;
            self.page_inited = 'undefined';
            window.clearTimeout(self.get_brake_list_timer);
            var sort_value = self.sort_direction + self.sort_field;
            self.get_brake_list_timer = setTimeout(function(){self.get_brake_list(self.page_no, sort_value)}, 400);
        },

        'click .search-brake': function () {
            $('.add-brake').addClass('hide');
            var self = this;
            self.page_no = 1;
            self.page_inited = 'undefined';
            var sort_value = this.sort_direction + this.sort_field;
            this.get_brake_list(self.page_no, sort_value);
        },

        'change .add-brake-type': function () {
            $('.add-brake-city').change();
        },

        'change .add-brake-city': function () {
            $('.add-brake-project').html('<option value="">--楼盘--</option>');
            $('.add-brake-project').val('');
            $('.project_select_input').val('');
            $('.add-brake-project').change();
            if (!$('.add-brake-city').val()) {
                return true;
            }
            $.ajax({
                url: '/basedata_api/Basedata_Project_Api/get_project_list_by_city/',
                type: 'POST',
                data: {
                    province: $('.add-brake-province').val(),
                    city: $('.add-brake-city').val()
                },
                dataType: 'json',
                success: function (result) {
                    var project_list = result.data.project_list;
                    UI.createSimpleOption($('.add-brake-project'), project_list);
                }
            });
        },

        'change .add-brake-project': function (event) {
            $('.add-brake-group').val('');
            $('.add-brake-build').val('');
            $('.group-block').addClass('hide');
            $('.build-block').addClass('hide');
            $('.unit-block').addClass('hide');
            var view = this;
            if (!$('.add-brake-project').val()) {
                return true;
            }
            $.ajax({
                url: '/basedata_api/Basedata_Group_Api/get_group_list/',
                type: 'POST',
                data: {
                    province: $('.add-brake-province').val(),
                    city: $('.add-brake-city').val(),
                    project: $('.add-brake-project').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var group_list = result.data.group_list;
                    if (group_list.length == 0) {
                        $('.group-block').addClass('hide');
                        $('.build-block').removeClass('hide');
                        $('.unit-block').addClass('hide');
                        $('.add-brake-build').html('<option value="">-- 楼栋 --</option>');
                        view.get_build_list();
                    } else {
                        $('.unit-block').addClass('hide');
                        $('.build-block').addClass('hide');
                        $('.group-block').removeClass('hide');
                        $('.add-brake-group').html('<option value="">-- 组团 --</option>');
                        var str = '';
                        for (var i = 0; i < group_list.length; i++) {
                            str += '<option value="' + group_list[i] + '">' + group_list[i] + '</option>';
                        }
                        $('.add-brake-group').append(str);
                    }
                }
            });
        },

        'change .add-brake-group': function () {
            var group = $('.add-brake-group').val();
            if (!group) {
                $('.build-block').addClass('hide');
                $('.unit-block').addClass('hide');
                $('.add-brake-build').val('');
                $('.add-brake-unit').val('');
                return true;
            }
            var view = this;
            $('.build-block').removeClass('hide');
            $('.unit-block').addClass('hide');
            $('.add-brake-build').val('');
            $('.add-brake-build').html('<option value="">-- 请选择楼栋 --</option>');
            view.get_build_list();
        },

        'change .add-brake-build': function () {
            var build = $('.add-brake-build').val();
            if (!build) {
                $('.unit-block').addClass('hide');
                $('.add-brake-unit').val('');
                return true;
            }
            $('.add-brake-unit').val('');
            $('.add-brake-unit').html('<option value="">-- 请选择单元 --</option>');
            $.ajax({
                url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
                type: 'POST',
                data: {
                    province: $('.add-brake-province').val(),
                    city: $('.add-brake-city').val(),
                    project: $('.add-brake-project').val(),
                    group: $('.add-brake-group').val(),
                    build: $('.add-brake-build').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var unit_list = result.data.unit_list;
                    if (unit_list.length != 0) {
                        $('.unit-block').removeClass('hide');
                        var str = '';
                        for (var i = 0; i < unit_list.length; i++) {
                            str += '<option value="' + unit_list[i] + '">' + unit_list[i] + '</option>';
                        }
                        $('.add-brake-unit').append(str);
                    }
                }
            });
        },

        'click .add-brake-btn': function () {
            var _this = this;
            var $modal = $('.add-brake');
            // 判断必填项是否为空
            if (!$('.add-brake select[name="province"]').val() ||
                !$('.add-brake select[name="city"]').val() ||
                !$('.add-brake select[name="project"]').val() ||
                !$('.add-brake input[name="mac"]').val() ||
                !$('.add-brake select[name="direction"]').val() ||
                !$('.add-brake input[name="gate_name"]').val()) {
                UI.showTips('danger', '请填写完整的信息');
                return false;
            }
            // 判断mac是否正确
            var mac_val = $('.add-brake input[name="mac"]').val();
            if (!this.reg_mac.test(mac_val) && !this.reg_mac_two.test(mac_val)) {
                UI.showTips('danger', '请填写正的mac地址');
                return false;
            }
            // 判断RSI是否正确
            var bluetooth_rsi_val = $('.add-brake input[name="bluetooth"]').val();
            var wifi_rsi_val = $('.add-brake input[name="wifi"]').val();
            if (!this.checkBrakeInput($modal, 'bluetooth', '请填写正确的蓝牙 RSI')) {
                return false;
            }
            if (!this.checkBrakeInput($modal, 'wifi', '请填写正确的wifi RSI')) {
                return false;
            }

            // 判断开门时间
            if (!this.checkBrakeInput($modal, 'opentime', '请填写正确的开门时间', true)) {
                return false;
            }

            $('.add-brake-btn').button('loading');

            $.ajax({
                url: '/brake_api/Brake_Machine_Api/add_brake/1/',
                type: 'POST',
                context: this,
                data: {
                    province: $('.add-brake select[name="province"]').val(),
                    city: $('.add-brake select[name="city"]').val(),
                    project: $('.add-brake select[name="project"]').val(),
                    group: $('.add-brake select[name="group"]').val(),
                    build: $('.add-brake select[name="build"]').val(),
                    unit: $('.add-brake select[name="unit"]').val(),
                    mac: $('.add-brake input[name="mac"]').val(),
                    gate_name: $('.add-brake input[name="gate_name"]').val(),
                    direction: $('.add-brake select[name="direction"]').val(),
                    bluetooth_rssi: $('.add-brake input[name="bluetooth"]').val(),
                    wifi_rssi: $('.add-brake input[name="wifi"]').val(),
                    open_time: $('.add-brake input[name="opentime"]').val(),
                },
                dataType: 'json',
                success: function (result) {
                    $('.add-brake-btn').button('reset');

                    if (result.data.flag != "Y") {
                        UI.showTips('danger', result.msg);
                        return false;
                    }

                    // $('.add-brake form').resetForm();
                    UI.showTips('info', '添加成功');
                }
            });
        },

        'click .edit-brake-btn': function (event) {
            var item = $(event.srcElement || event.target).parents('tr.brake-item');
            $.ajax({
                url: '/brake_api/Brake_Machine_Api/get_brake_info/1/',
                type: 'POST',
                data: {
                    brake_id: item.data('brake-id')
                },
                dataType: 'json',
                context: this,
                success: function (result) {
                    if (result.data.flag == "Y") {
                        var brake = result.data.brake;
                        var version_list = result.data.brake_version_list;
                        $('#edit_brake_modal input[name="edit-brake_id"]').val(brake.id);
                        $('#edit_brake_modal input[name="bluetooth"]').val(brake.bluetooth_rssi);
                        $('#edit_brake_modal input[name="wifi"]').val(brake.wifi_rssi);
                        $('#edit_brake_modal input[name="opentime"]').val(brake.open_time);
                        $('#edit_brake_modal input[name="level"]').val(brake.position.level);
                        UI.createOption($('.change-brake-version'),version_list,"id","version",brake.version_id);
                        $('#edit_brake_modal').modal('show');
                    } else {
                        UI.showTips('danger', result.msg);
                    }
                }
            });

        },

        'change .edit-brake-province': function () {
            $('.edit-brake-city').html('<option value="">-- 请选择城市 --</option>');
            $('.edit-brake-city').val('');
            $('.edit-brake-city').change();

            if (!$('.edit-brake-province').val()) {
                return true;
            }

            $.ajax({
                url: ' /geo_api/Geo_Api/get_city_list/1/',
                type: 'POST',
                data: {
                    province: $('.edit-brake-province').val(),
                },
                dataType: 'json',
                success: function (result) {
                    var city_list = result.data.city_list;
                    for (var i = 0; i < city_list.length; i++) {
                        var option = $('<option></option>');
                        option.attr('value', city_list[i]);
                        option.html(city_list[i]);
                        $('#edit_brake_modal .edit-brake-city').append(option);
                    }
                }
            });
        },

        'change .edit-brake-city': function () {
            $('.edit-brake-community').html('<option value="">-- 请选择小区 --</option>');
            $('.edit-brake-community').val('');
            $('.project_select_input').val('');
            $('.edit-brake-community').change();

            if (!$('.edit-brake-city').val()) {
                return true;
            }

            $.ajax({
                url: '/geo_api/Geo_Api/get_community_list/1/',
                type: 'POST',
                data: {
                    province: $('.edit-brake-province').val(),
                    city: $('.edit-brake-city').val()
                },
                dataType: 'json',
                success: function (result) {
                    var community_list = result.data.community_list;

                    for (var i = 0; i < community_list.length; i++) {
                        var option = $('<option></option>');
                        option.attr('value', community_list[i]);
                        option.html(community_list[i]);
                        $('.edit-brake-community').append(option);
                    }
                }
            });
        },

        'change .edit-brake-community': function () {
            $('.edit-brake-gate').html('<option value="">-- 请选择位置 --</option>');
            $('.edit-brake-gate').val('');

            if (!$('.edit-brake-community').val()) {
                return true;
            }

            $.ajax({
                url: '/geo_api/Geo_Api/get_gate_list/1/',
                type: 'POST',
                data: {
                    province: $('.edit-brake-province').val(),
                    city: $('.edit-brake-city').val(),
                    community: $('.edit-brake-community').val(),
                    gate_type: $('.edit-brake-type').val()
                },
                dataType: 'json',
                success: function (result) {
                    var gate_list = result.data.gate_list;
                    for (var i = 0; i < gate_list.length; i++) {
                        var option = $('<option></option>');
                        option.attr('value', gate_list[i].gate_id);
                        option.html(gate_list[i].position);
                        $('.edit-brake-gate').append(option);
                    }
                }
            });
        },

        'click .submit-brake-btn': function () {
            var self = this;
            if (!$('#edit_brake_modal input[name="bluetooth"]').val() ||
                !$('#edit_brake_modal input[name="wifi"]').val() ||
                !$('#edit_brake_modal input[name="opentime"]').val()) {
                UI.showTips('danger', '请填写完整的信息');
                return false;
            }

            var $modal = $('#edit_brake_modal');

            if (!this.checkBrakeInput($modal, 'bluetooth', '请填写正确的蓝牙 RSI')) {
                return false;
            }
            if (!this.checkBrakeInput($modal, 'wifi', '请填写正确的wifi RSI')) {
                return false;
            }
            if (!this.checkBrakeInput($modal, 'opentime', '请填写正确的开门时间', true)) {
                return false;
            }

            $.ajax({
                url: '/brake_api/Brake_Machine_Api/submit_brake/1/',
                type: 'POST',
                context: this,
                data: {
                    brake_id: $modal.find('input[name="edit-brake_id"]').val(),
                    bluetooth_rssi: $modal.find('input[name="bluetooth"]').val(),
                    wifi_rssi: $modal.find('input[name="wifi"]').val(),
                    open_time: $modal.find('input[name="opentime"]').val(),
                    level: $modal.find('input[name="level"]').val(),
                    version_id: $modal.find('select[name="version"]').val(),
                },
                dataType: 'json',
                success: function (result) {
                    if (result.data.flag != "Y") {
                        UI.showTips('danger', result.msg);
                        return false;
                    }
                    $modal.modal('hide');
                    UI.showTips('info', '提交成功');
                    this.get_brake_list(self.page_no, "created_time");
                }
            });
        },

        'click .remove-brake-btn': function (event) {
            if (!confirm('确定要删除吗？')) return true;

            var item = $(event.srcElement || event.target).parents('tr.brake-item');

            $.ajax({
                url: '/brake_api/Brake_Machine_Api/delete_brake/1/',
                type: 'POST',
                context: this,
                data: {
                    brake_id: item.data('brake-id')
                },
                dataType: 'json',
                success: function (result) {
                    item.remove();
                    UI.showTips('info', '删除成功');
                }
            });
        },

        'click .dump-brake-btn': function () {
              $("#dump_data_modal span.dump_data_type").text('brake_machine');
              $("#dump_data_modal").modal('show');
//            var _this = this;
//            var data = {
//                province: $(_this.el).find('.search-brake-province').val(),
//                city: $(_this.el).find('.search-brake-city').val(),
//                project: $(_this.el).find('.project_select_input').val(),
//                group: $(_this.el).find('.search-brake-group').val(),
//                build: $(_this.el).find(".search-brake-build").val(),
//                unit: $(_this.el).find(".search-brake-unit").val(),
//                firmware_version: $(_this.el).find(".search-brake-firmware").val(),
//                hardware_version: $(_this.el).find(".search-brake-hardware").val(),
//                lately_pass: $(_this.el).find(".search-brake-pass").val(),
//            }
//            var get_str = $.param(data);
//            $.ajax({
//                url: '/brake_api/Brake_Machine_Api/dump_brake_machine/',
//                type: 'POST',
//                data: data,
//                dataType: 'json',
//                success: function(result){
//                    if(result.data.flag == 'N') {
//                        UI.showErrTip("正在准备数据，请稍候");
//                    }else{
//                        var url = '/dump_brake_machine_to_excel?' + get_str;
//                        window.location.href = url;
//                    }
//                }
//            });
        },

        'click th.sortable':function(evt){
            var field = $(evt.currentTarget).closest('th').data('field');
            var direction = $(evt.currentTarget).closest('th').data('direction');
            if(direction=='-'){
                direction = '';
            }else{
                direction= '-';
            }

            this.sort_field = field;
            this.sort_direction = direction;

            this.get_brake_list(this.page_no, direction + field);
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
            if(!!!$(evt.target).val()){
                $(evt.target).siblings("select").val("");
                $(evt.target).siblings("select").change();
            }
        },

        'click .project_select_ul>li':function(evt){
            var project = $(evt.target).text();
            var select_obj = $(evt.target).parent("ul").siblings("select");
            $(".project_select_input").val(project);
            var select_list = select_obj.find("option");

            select_obj.val(project);
            select_obj.change();

            $(evt.target).parent("ul").html("").hide();
        },
    }
});

