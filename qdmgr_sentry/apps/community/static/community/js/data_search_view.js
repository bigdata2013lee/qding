(function ($) {


    var views = qd.nameSpace('Views');

    var view1 = Backbone.View.extend({
        main_template: versionify(CONST.static_url + 'community/ejs/data_search_by_phone_block.html'),
        extend_template: versionify(CONST.static_url + 'community/ejs/data_search_by_phone.template'),
        initialize: function () {
            $(this.el).html(new EJS({url: this.main_template}).render());
            $(this.el).find('.template_div:first').load(this.extend_template);
        },

        events: {
            'click div.operate-box button.query': function (evt) {
                var self = this;
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                if (params.phone_no == '' || !/^\s*1\d{10}\s*$/.test(params.phone_no)) {
                    UI.showErrTip("请输入正确的手机号");
                    return;
                }
                self.exec_query(params.phone_no);
            },

            'click div.operate-box button.update': function(){
                var self = this;
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                if (params.phone_no == '' || !/^\s*1\d{10}\s*$/.test(params.phone_no)) {
                    UI.showErrTip("请输入正确的手机号");
                    return;
                }
                self.exec_update(params.phone_no);
            },

            'click th.sortable-pass':function(evt){
                var field = $(evt.currentTarget).closest('th').data('field');
                var direction = $(evt.currentTarget).closest('th').data('direction');
                if(direction=='-'){
                    direction = '';
                }else{
                    direction= '-';
                }

                this.sort_field = field;
                this.sort_direction = direction;
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));

                this.query_tx_rec(params.phone_no, direction, field);
            },

            'click th.sortable-brake':function(evt){
                var field = $(evt.currentTarget).closest('th').data('field');
                var direction = $(evt.currentTarget).closest('th').data('direction');
                if(direction == '-'){
                    direction = '';
                }else{
                    direction = '-';
                }
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                this.query_brake_devices(params.phone_no, direction, field);
            },

            'click th.sortable-room':function(evt){
                var direction = $(evt.currentTarget).closest('th').data('direction');
                if(direction == '-'){
                    direction = '';
                }else{
                    direction = '-';
                }
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                this.query_bind_rooms(params.phone_no, direction);
            },
        },

        query_tx_rec: function (phone_no, sort_direction, sort_field) {
            var self = this;

            var sort = sort_direction+sort_field;
            var data_flag = $("input:radio[name='data_flag']:checked").val();
            var rpc_url = '/brake_api/Brake_Pass_Api/get_user_try_pass_list_by_phone/1/';
            if(data_flag=="1"){
                rpc_url = '/brake_api/Brake_Pass_Api/get_user_pass_list_by_phone/1/';
            }

            qd.brake_rpc(rpc_url,{phone: phone_no, sorted_field: sort})
                .success(function (result) {
                    result.sort_direction = sort_direction;
                    result.sort_field = sort_field;
                    qd.render_template('tx_rec', result, $(self.el).find('.tab-content>div#tab_a1'));
                })
        },

        query_brake_devices: function (phone_no, sort_direction, sort_field) {
            var self = this;
            qd.brake_rpc('/basedata_api/Basedata_Bj_App_User_Api/get_app_user_can_open_door/1/',
                {phone: phone_no, sorted_field: sort_field, sorted_direction: sort_direction})
                .success(function (result) {
                    result.sort_direction = sort_direction;
                    result.sort_field = sort_field;
                    qd.render_template('brake_device', result, $(self.el).find('.tab-content>div#tab_a3'));
                })
        },

        query_bind_rooms: function (phone_no, sorted_direction) {
            var self = this;
            qd.brake_rpc('/basedata_api/Basedata_Bj_App_User_Api/get_app_user_bind_room_list/1/',
                {phone: phone_no, sorted_direction: sorted_direction})
                .success(function (result) {
                    result.sort_direction = sorted_direction;
                    qd.render_template('bind_rooms', result, $(self.el).find('.tab-content>div#tab_a4'));
                })
        },

        exec_query: function (phone_no) {
            var self = this;
            $(self.el).find('.tab-content>div').html('<center style="margin:4em; color: #808080;">正在加载，请稍后...</center>');
            self.query_tx_rec(phone_no, "-", "updated_time");
            self.query_brake_devices(phone_no, "", "position_str");
            self.query_bind_rooms(phone_no, "");
        },

        exec_update: function (phone_no) {
            qd.brake_rpc('/basedata_api/Basedata_Bj_App_User_Api/set_app_user_room_list_now/', {phone: phone_no})
                .success(function(result){
                    if(result.data.flag == 'N') {
                        UI.showErrTip(result.msg);
                    }else {
                        UI.showSucTip("更新成功");
                    }
                })
        },
    });


    var view2 = Backbone.View.extend({
        main_template: versionify(CONST.static_url + 'community/ejs/data_search_by_machine_block.html'),
        extend_template: versionify(CONST.static_url + 'community/ejs/data_search_by_machine.template'),
        initialize: function () {
            var xxxhtml = new EJS({url: this.main_template}).render();
            $(this.el).html(xxxhtml);
            $(this.el).find('.template_div:first').load(this.extend_template);
            $(this.el).find("#machine_select_modal").qdui_autocomplete_win();
        },

        events: {
            'click div.operate-box .search-brake-btn': function (evt) {
                var self = this;
                var mac = $(self.el).find(".sss_input.machine li").data('obj_mac');
                if (!mac) {
                    return false
                }
                self.exec_query(mac);
            },

            //捕获窗口的选择事件
            'select_item #machine_select_modal': function (evt, li_el) {
                var self = this;
                var select_name = $(evt.currentTarget).find('.qdui_autocomplete').data('select_for');
                var sss_input = $(self.el).find('.sss_input[select_name=' + select_name + ']');
                var clone_li = $.clone(li_el);
                sss_input.html('');
                sss_input.append(clone_li);
                var mac = $(sss_input).find('li').data('obj_mac');
                this.exec_query(mac);
            },

            'click .operate-box .sss_input.machine': function (evt) {
                $(this.el).find('#machine_select_modal').modal('show');
                var province = $("#sProvince").text();
                var city = $("#sCity").text();
                var project = $("#sCommunity").text();
                this._load_machines(province, city, project);
            }
        },

        query_tx_rec: function (mac) {
            var self = this;
            qd.brake_rpc('/brake_api/Brake_Pass_Api/get_brake_pass_list/1/', {mac: mac})
                .success(function (result) {
                    qd.render_template('tx_rec', result, $(self.el).find('.tab-content>div#tab_a1'));
                })
        },


        exec_query: function (mac) {
            var self = this;

            $(self.el).find('.tab-content>div').html('<center style="margin:4em; color: #808080;">正在加载，请稍后...</center>');
            self.query_tx_rec(mac);
        },


        _load_machines: function (province, city, project) {
            var self = this;
            $(self.el).find('.qdui_autocomplete.machine .list_div').html('<center>正在加载...</center>');
            qd.brake_rpc('/brake_api/Brake_Machine_Api/get_brake_machine_by_filter/1/', {
                    province: province,
                    city: city,
                    project: project
                })
                .success(function (result) {
                    setTimeout(function () {
                        qd.render_template('machine_list', result, $(self.el).find('.qdui_autocomplete.machine .list_div'));
                    }, 1000 * 2);
                })
        }


    });

    var view3 = Backbone.View.extend({
        main_template:versionify(CONST.static_url + 'community/ejs/data_search_by_card_block.html'),
        extend_template:versionify(CONST.static_url + 'community/ejs/data_search_by_card.template'),
        initialize: function(){
            $(this.el).html(new EJS({url: this.main_template}).render());
            $(this.el).find('.template_div:first').load(this.extend_template);
        },
        events: {
            'click div.operate-box button.query': function (evt) {
                var self = this;
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                var card_no = $.trim(params.card_no);
                if (card_no == '' || !/^\d*$/.test(card_no)) {
                    UI.showErrTip("请输入正确的门禁卡号");
                    return;
                }
                self.exec_query(params.card_no);
            },
            'click div.operate-box button.update': function(){
                var self = this;
                var params = qd.utils.serialize($(this.el).find('div.operate-box'));
                var card_no = $.trim(params.card_no);
                if (card_no == '' || !/^\d*$/.test(card_no)) {
                    UI.showErrTip("请输入正确的门禁卡号");
                    return;
                }
                self.exec_update(params.card_no);
                self.exec_query(params.card_no);
            },
        },

        exec_query: function (card_no) {
            var self = this;
            $(self.el).find('.tab-content>div').html('<center style="margin:4em; color: #808080;">正在加载，请稍后...</center>');
            self.query_card_info(card_no);
            self.query_brake_devices(card_no);
            self.query_tx_rec(card_no);
        },

        exec_update: function (card_no) {
            qd.brake_rpc('/brake_api/Brake_Card_Api/set_can_open_door_list/', {card_no: card_no})
                .success(function(result){
                    if(result.data.flag == 'N') {
                        UI.showErrTip(result.msg);
                    }else {
                        UI.showSucTip("更新成功");
                    }
                })
        },

        query_tx_rec: function (card_no) {
            var self = this;

            var data_flag = $("input:radio[name='data_flag']:checked").val();
            var rpc_url = '/brake_api/Brake_Pass_Api/get_user_try_pass_list_by_card/';
            if(data_flag=="1"){
                rpc_url = '/brake_api/Brake_Pass_Api/get_user_pass_list_by_card/';
            }

            qd.brake_rpc(rpc_url,
                {card_no: card_no, page_size: 10})
                .success(function (result) {
                    qd.render_template('tx_rec', result, $(self.el).find('.tab-content>div#tab_a1'));
                })
        },

        query_brake_devices: function (card_no) {
            var self = this;
            qd.brake_rpc('/brake_api/Brake_Card_Api/get_can_open_door_list/',
                {card_no: card_no})
                .success(function (result) {
                    qd.render_template('brake_device', result, $(self.el).find('.tab-content>div#tab_a3'));
                })
        },

        query_card_info: function (card_no) {
            var self = this;

            qd.brake_rpc('/brake_api/Brake_Card_Api/get_card_info/',
                {card_no: card_no})
                .success(function (result) {
                    qd.render_template('card_info', result, $(self.el).find('.tab-content>div#tab_a4'));
                })
        },
    });

    var view4 = Backbone.View.extend({
        main_template:versionify(CONST.static_url + 'community/ejs/data_search_failed_pass_data_block.html'),
        extend_template:versionify(CONST.static_url + 'community/ejs/data_search_failed_pass_data.template'),
        page_no: 1,
        page_size: 30,
        page_inited: false,
        group_list:null,
        get_list_timer: 0,

        initialize: function(){
            $(this.el).html(new EJS({url: this.main_template}).render());
            $(this.el).find('.template_div:first').load(this.extend_template);
            var view = this;
            view.loadData();
            $(this.el).find('.pass-data-date').datetimepicker({
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

        loadData: function () {
            this.getGroupList();
            this.getBuildList();
            this.getList()
        },

        getList: function (pageIndex) {
            if (typeof pageIndex == "undefined") {
                this.page_no = 1;
                this.page_inited = false;
            }
            var _this = this;

            var start_time = new Date($('.start-time').val()).getTime() / 1000;
            var end_time = new Date($('.end-time').val()).getTime() / 1000;

            if (start_time && end_time) {
                if(start_time*1 >= end_time*1){
                    UI.showErrTip("结束时间必须比开始时间晚");
                    return false;
                }
            }

            if(!!!start_time){
                start_time = '';
            }

            if(!!!end_time){
                end_time = '';
            }

            qd.brake_rpc('/brake_api/Brake_Pass_Api/get_failed_user_try_pass_list/1/',
                {
                    pass_type: $('.pass-data-type').val(),
                    page_no: _this.page_no,
                    page_size: _this.page_size,
                    province: $("#sProvince").html(),
                    city: $("#sCity").html(),
                    project: $("#sCommunity").html(),
                    group: $(".pass-data-group").val(),
                    build: $(".pass-data-build").val(),
                    unit: $(".pass-data-unit").val(),
                    mac: $(".pass-data-mac").val(),
                    phone: $(".pass-data-phone").val(),
                    start_time: start_time,
                    end_time: end_time})
                .success(function (result) {
                    qd.render_template('failed_pass_list', result, $(_this.el).find('.failed-pass-data-list'));
                    if (result.data.pagination) {
                        if (!_this.page_inited) {
                            _this.initPager(result.data.pagination.total_count);
                        }
                    }
                })
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

            'change .pass-data-type': function () {
                $(".pass-data-phone").val('');
                var pass_type = $(".pass-data-type").val();
                if(pass_type == "10"){
                    $(".pass-data-phone").attr("placeholder", "卡号");
                }else{
                    $(".pass-data-phone").attr("placeholder", "手机号");
                }
            },

            'click .pass-data-query': function () {
                this.getList();
            },

//            'change .pass-data-unit':function(){
//                this.getList();
//            },
//            'keyup .pass-data-mac': function() {
//                this.get_list_timer =setTimeout(function(){this.getList()}, 400);
//            },
//
//            'keyup .pass-data-phone': function() {
//                this.get_list_timer =setTimeout(function(){this.getList()}, 400);
//            },
//
//            'change .start-time':function(){
//                this.getList();
//            },
//
//            'change .end-time':function(){
//                this.getList();
//            },
        }
    });

    views.DataSearchByPhoneView = view1;
    views.DataSearchByMachineView = view2;
    views.DataSearchByCardView = view3;
    views.DataSearchFailedPassDataView = view4;

})(jQuery)