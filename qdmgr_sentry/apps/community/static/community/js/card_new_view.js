window._qd_card_reader = {
    _inited: false,

    _init_ws: function () {
        var wsUri = "ws://127.0.0.1:8777/";
        var ws = this.ws = new WebSocket(wsUri);

        ws.onmessage = function (evt) {
            var data = JSON.parse(evt.data);
            if ("invoke" in data) {
                $(document).trigger("invoke/" + data.invoke, data.result);
            }
        };

        ws.onopen = function (evt) {
        };
        ws.onclose = function () {
            UI.showErrTip('请打开千丁读卡器程序后重试！');
        };
        ws.onerror = function (evt) {
        };

        this.bind_read_write_card();
        this._inited = true;
    },

    invoke: function (method, params) {
        if (!params) {
            params = {};
        }
        if(this.ws.readyState!=1){UI.showErrTip('请先打开千丁读卡器程序！');}
        this.ws.send(JSON.stringify({method: method, params: params}));
    },

    bind_read_write_card: function () {
        $(document).bind("invoke/read_card", function (evt, result) {
            if (!!!_card_new_view.checkCardSn(result)) {
                _card_new_view.reset_card_info();
                $('.card-new-no').val('');
            } else {
                $('input.card-new-no').val(parseInt(result,16));
                _card_new_view.readCard(result, parseInt(result,16));
            }
        });
        $(document).bind("invoke/write_card", function (evt, result) {
            if (result === 0) {
                _card_new_view.open_card();
            }
        });
    }
};


var card_new_view = Backbone.View.extend({
        className: 'card_new_view',
        template: versionify(CONST.static_url + 'community/ejs/card_new_block.html'),
        card_info: null,
        id_info: null,
        owner_info: null,
        write_no: null,
        write_flag: false,
        addIndex: 0,
        group_list: [],
        build_list: [],
        flag: false,


        initialize: function () {
            $(this.el).html(new EJS({url: this.template}).render({}));
            window._card_new_view = this;
            this.loadData();
            if (!!!window._qd_card_reader._inited) {
                window._qd_card_reader._init_ws();
            };
            setTimeout(function(){
                $('.card-new-validity-div').datetimepicker({
                    format: "yyyy/mm/dd",
                    autoclose: true,
                    todayBtn: false,
                    pickerPosition: "bottom-left",
                    minView: 2,
                    language: 'zh-CN',
                });
            }, 1000*1);
        },

        loadData: function () {
            this.getGroupList();
            this.initData();
        },

        initData: function() {
            this.card_info = null;
            this.id_info = null;
            this.owner_info = null;
            this.write_no = null;
            this.write_flag = null;
            this.addIndex = 0;
            $('.add-room-list').remove();
        },

        reset_card_info: function () {
            this.getGroupList();
            $('.write-card-btn').html('发卡');
            $('.card-new-validity').val('');
            var html_str = '<option value="">性别</option>';
            html_str += '<option value="M">男</option>';
            html_str += '<option value="F">女</option>';
            $('.card-new-gender').html(html_str);
            $('.card-new-username').val('');
            $('.card-new-phone').val('');
        },

        checkCardSn: function (card_sn) {
            if (!!!card_sn) {
                UI.showErrTip('未能读取到卡号，请重试');
                return false;
            } else if (card_sn == '1') {
                UI.showErrTip('未发现发卡器，请连接发卡器');
                return false;
            } else if (card_sn == '2') {
                UI.showErrTip('通讯失败，请重试');
                return false;
            } else if (card_sn == '3') {
                UI.showErrTip('未检测到卡片，请将卡片平放于发卡器');
                return false;
            }
            return true;
        },

        set_card_obj_info: function () {
            var self = this;
            var card_no = $('.card-new-no').val();
            var enc_card_no = $('.card-new-enc-no').val();
            var enc_card_no_count = $('.card-new-enc-no-count').val();
            var card_type = $('.card-new-type').val();
            var card_type_str = $('.card-new-type').children("option:selected").text();
            var card_validity = $('.card-new-validity').val();
            if(!!card_validity){
                card_validity = new Date(card_validity).getTime().toString().substr(0,10);
            }
            var project_id = $('#sProjectId').html();
            var group_id = $('.card-new-group').val();
            var build_id = $('.card-new-build').val();
            var unit_id = $('.card-new-unit').val();
            var room_id = $('.card-new-room').val();
            var gender = $('.card-new-gender').val();
            var gender_str = $('.card-new-gender').children("option:selected").text();
            var username = $('.card-new-username').val();
            var phone = $('.card-new-phone').val();
            var owner_type = $('.card-new-owner-type').val();
            var owner_type_str = $('.card-new-owner-type').children("option:selected").text()
            var owner_role = $('.card-new-owner-role').val();
            var owner_role_str = $('.card-new-owner-role').children("option:selected").text()
            var owner_age = $('.card-new-owner-age').val();
            var owner_age_str = $('.card-new-owner-age').children("option:selected").text()
            var owner_family_structure = $('.card-new-owner-family-structure').val();
            var owner_family_structure_str = $('.card-new-owner-family-structure').children("option:selected").text()

            this.card_info = {
                'enc_card_no': enc_card_no,
                'enc_card_no_count': enc_card_no_count,
                'card_no': card_no,
                'card_type': card_type,
                'card_validity': card_validity,
            };
            this.id_info = {
                'project_id_list': [{
                    'project_id': project_id,
                    'group_id': group_id,
                    'build_id': build_id,
                    'unit_id': unit_id,
                }],
                'room_id_list': self.get_room_ids(),
            };
            this.owner_info = {
                'name': username,
                'phone': phone,
                'gender': gender,
                'gender_str': gender_str,
                'type': owner_type,
                'type_str': owner_type_str,
                'age': owner_age,
                'age_str': owner_age_str,
                'role': owner_role,
                'role_str': owner_role_str,
                'family_structure': owner_family_structure,
                'family_structure_str': owner_family_structure_str,
            };
        },

        check_card_obj_info: function () {
            this.set_card_obj_info();
            if (!!!this.id_info || !!!this.card_info) {
                UI.showErrTip('未能获取到正确信息，请联系管理员');
                return false;
            }
            if (!!!this.id_info.project_id_list) {
                UI.showErrTip('未能获取到基础数据，请重试');
                return false;
            }
            if (!!!this.id_info.project_id_list[0].project_id) {
                UI.showErrTip('未能获取到项目信息，请重新登录');
                return false;
            }
            var card_no = this.card_info.card_no;
            if (!!!card_no) {
                UI.showErrTip('卡号不能为空');
                return false;
            }
            var enc_card_no_count = this.card_info.enc_card_no_count;
            var enc_card_no = this.card_info.enc_card_no;
            if (enc_card_no_count === null || !!!enc_card_no) {
                UI.showErrTip('未能获取正确卡号，请联系管理员');
                return false;
            }
            if (!!!this.card_info.card_type) {
                UI.showErrTip('请选择卡类型');
                return false;
            }
            if(this.card_info.card_type=='5'){
                if (!!!this.id_info.project_id_list[0].build_id) {
                    UI.showErrTip('请选择楼栋信息');
                    return false;
                }
                if (!!!this.id_info.project_id_list[0].unit_id) {
                    UI.showErrTip('请选择单元信息');
                    return false;
                }
            }
            if (this.flag){
               return false;
            }
            if (this.card_info.card_type == '5' && !!!this.id_info.room_id_list[0] && this.id_info.room_id_list.length==0) {
                UI.showErrTip('房屋信息不正确');
                return false;
            }

            if (!!this.owner_info.phone && !!!qd.utils.isVaildPhone(this.owner_info.phone)) {
                UI.showErrTip('请填写正确的手机号码');
                return false;
            }
            return true;
        },

        get_write_no_and_open_card: function () {
            var self = this;
            $.ajax({
                url: '/brake_api/Brake_Card_Api/get_write_no/1/',
                type: 'POST',
                data: {
                    card_info: JSON.stringify(self.card_info),
                    id_info: JSON.stringify(self.id_info),
                },
                dataType: 'json',
                success: function (result) {
                    if (result.data.flag == 'Y') {
                        var write_no = result.data.write_no;
                        window._qd_card_reader.invoke("write_card", {str_data: write_no});
                    } else {
                        UI.showErrTip(result.msg);
                    }
                }
            });
        },

        open_card: function () {
            var self = this;
            $.ajax({
                url: '/brake_api/Brake_Card_Api/open_card/1/',
                type: 'POST',
                data: {
                    card_info: JSON.stringify(self.card_info),
                    id_info: JSON.stringify(self.id_info),
                    owner_info: JSON.stringify(self.owner_info),
                },
                dataType: 'json',
                success: function (result) {
                    if (result.data.flag == 'Y') {
                        UI.showSucTip('恭喜！！！发卡成功');
                    } else {
                        UI.showErrTip('发卡失败' + result.msg);
                    }
                    self.id_info = null;
                    self.card_info = null;
                    self.owner_info = null;
                }
            });
        },

        readCard: function (card_sn, card_no) {
            var self = this;
            $.ajax({
                url: '/brake_api/Brake_Card_Api/read_card/1/',
                type: 'POST',
                data: {
                    card_sn: card_sn,
                    card_no: card_no,
                },
                dataType: 'json',
                success: function (result) {
                    var enc_card_no = result.data.enc_card_no;
                    var enc_card_no_count = result.data.count;
                    $('.card-new-enc-no').val(enc_card_no);
                    $('.card-new-enc-no-count').val(enc_card_no_count);
                    if (result.data.flag == 'Y') {
                        if (self.write_flag) {
                            if (!/不存在/.test(result.msg)){
                                var card_obj_info = result.data.card_obj_info;
                                console.info(card_obj_info);
                                var card_area = card_obj_info.card_area;
                                var card_area_str = card_area[0]['project']
                                if(card_area[0]['group']){card_area_str += '-' + card_area[0]['group'];}
                                if(card_area[0]['build']){card_area_str += '-' + card_area[0]['build'] + '栋';}
                                if(card_area[0]['unit']){card_area_str += '-' + card_area[0]['unit'] + '单元';}
                                if(card_area[0]['room']){card_area_str += '-' + card_area[0]['room'];}
                                if(!confirm('此卡已发到'+ card_area_str+', 确定重发吗？')){
                                    return false;
                                }
                            }
                            if (!!self.check_card_obj_info()) {
                                self.get_write_no_and_open_card();
                            }
                        } else {
                            if (/不存在/.test(result.msg)) {
                                UI.showSucTip('这是新卡，请填写完整信息后，再选择发卡');
                                self.reset_card_info();
                            } else {
                                var card_obj_info = result.data.card_obj_info;
                                var card_area = card_obj_info.card_area;
                                var card_owner = card_obj_info.card_owner;
                                var project_id = $('#sProjectId').html();
                                var card_validity = card_obj_info.card_validity;
                                var card_type = card_obj_info.card_type;
                                $('.add-room-list').remove();
                                for (var i = 0; i < card_area.length; i++) {
                                    if(i!=0){self.createRoom();}
                                    if (card_area[i].project_id == project_id) {
                                        if (card_validity) {
                                            if (card_validity === 4294967295) {
                                                html_str = '';
                                            } else {
                                                var card_date = new Date(card_validity * 1000).format("yyyy/MM/dd");
                                                html_str = card_date;
                                            }
                                            $('.card-new-validity').val(html_str);
                                        }
                                        $('.card-new-type').val(card_type);
                                        $('.card-new-type').change();
                                        var base_data = card_area[i];
                                        var group = "";
                                        var group_id = "";
                                        if (base_data.group) {
                                            group = base_data.group;
                                        }
                                        if (base_data.group_id) {
                                            group_id = base_data.group_id;
                                        }
                                        var build = "";
                                        var build_id = "";
                                        if (base_data.build) {
                                            build = base_data.build;
                                        }
                                        if (base_data.build_id) {
                                            build_id = base_data.build_id;
                                        }
                                        var unit = "";
                                        var unit_id = "";
                                        if (base_data.unit) {
                                            unit = base_data.unit;
                                        }
                                        if (base_data.unit_id) {
                                            unit_id = base_data.unit_id;
                                        }
                                        var room = "";
                                        var room_id = "";
                                        if (base_data.room) {
                                            room = base_data.room;
                                        }
                                        if (base_data.outer_room_id) {
                                            room_id = base_data.outer_room_id;
                                        }
                                        if (room != "" && room_id != "") {
                                            var html_str = '<option value=' + room_id + ' selected>' + room + '</option>>';
                                            html_str += '<option value="">房间</option>>';
                                            $('.card-new-room').html(html_str);
                                        }
                                        var gender = card_owner.gender;
                                        var name = card_owner.name;
                                        var phone = card_owner.phone;
                                        if (group != "" && group_id != "") {
                                            var html_str = '<option value=' + group_id + ' selected>' + group + '</option>>';
                                            html_str += '<option value="">组团</option>>';
                                            $('.card-new-group').html(html_str);
                                        }
                                        if (build != "" && build_id != "") {
                                            var html_str = '<option value=' + build_id + ' selected>' + build + '</option>>';
                                            html_str += '<option value="">楼栋</option>>';
                                            $('.card-new-build').html(html_str);
                                        }
                                        if (unit != "" && unit_id != "") {
                                            var html_str = '<option value=' + unit_id + ' selected>' + unit + '</option>>';
                                            html_str += '<option value="">单元</option>>';
                                            $('.card-new-unit').html(html_str);
                                        }
                                        if (gender != "") {
                                            if (gender == 'M') {
                                                var html_str = '<option value=' + gender + ' selected>男</option>>';
                                                html_str += '<option value="F">女</option>>';
                                            } else {
                                                var html_str = '<option value=' + gender + ' selected>女</option>>';
                                                html_str += '<option value="M">男</option>>';
                                            }
                                            $('.card-new-gender').html(html_str);
                                        } else {
                                            var html_str = '<option value="" selected>性别</option>>';
                                            html_str += '<option value="M">男</option>>';
                                            html_str += '<option value="F">女</option>>';
                                            $('.card-new-gender').html(html_str);
                                        }
                                        $('.card-new-username').val(name);
                                        $('.card-new-phone').val(phone);
                                        $('.card-new-owner-type').val(card_owner.type);
                                        $('.card-new-owner-role').val(card_owner.role);
                                        $('.card-new-owner-age').val(card_owner.age);
                                        $('.card-new-owner-family-structure').val(card_owner.family_structure);
                                        $('.write-card-btn').html("重置");
                                    } else {
                                        UI.showErrTip('此卡已被其他社区占用，请选择正确的社区或请更换卡');
                                        return false;
                                    }
                                }
                            }
                        }
                    }
                }
            })
        },

        getGroupList: function () {
            var self = this;
            $('.card-new-group').html('<option value="">组团</option>');
            $.ajax({
                url: '/basedata_api/Basedata_Group_Api/get_group_list_by_filter/1/',
                type: 'POST',
                data: {
                    project_id: $('#sProjectId').html(),
                },
                dataType: 'json',
                success: function (result) {
                    if (!!!result.data.group_list) {
                        return false;
                    }
                    var group_list = result.data.group_list;
                    self.group_list = group_list;
                    if (group_list.length > 0) {
                        if (group_list.length == 1) {
                            UI.createOption($('.card-new-group'), group_list, 'group_id', 'group', group_list[0]['group_id']);
                        } else {
                            UI.createOption($('.card-new-group'), group_list, 'group_id', 'group', "");
                        }
                    }
                    $('.card-new-group').change();
                }
            });
        },

        createRoom: function () {
            var self = this;
            var group_list = [{'group_id':"",'group':'组团'}];
            if(self.group_list.length!=0){ group_list = self.group_list;}
            var build_list = [{'build_id':"",'build':"楼"}];
            if(build_list){build_list = self.build_list;}
            var unit_list = [{"unit_id":"", "unit":""}];
            var apartment_list = [{"outer_room_id":"", "room":"房间"}];
            $("#edit-room").append(self.createSelectedOption(group_list, build_list, unit_list, apartment_list));
            $('.add-room-list select[name=group]:last').change();
        },

        createSelectedOption: function(group_list,build_list,unit_list,room_list) {
            var val='';
            var str = '';
            str += '<div class="form-group clearfix select-room-list add-room-list"  id="room_'+ this.addIndex +'">';
            str += '	<div class="col-xs-3">';
            str += '		<select class="form-control" name="group">';
            for (var i = 0; i < group_list.length; i++) {
                val = group_list[i];
                str += '<option value="' + val.group_id + '"';
                if (i == 0) {
                    str += " selected";
                }
                str += '>'+ val.group + '</option>';
            }
            str += '		</select>';
            str += '	</div>';
            str += '	<div class="col-xs-3">';
            str += '		<select class="form-control" name="build">';
            for (var i = 0; i < build_list.length; i++) {
                val = build_list[i];
                str += '<option value="' + val.build_id + '"';
                if (i == 0) {
                    str += " selected";
                }
                str += '>'+ val.build + '栋</option>';
            }
            str += '		</select>';
            str += '	</div>';
            str += '	<div class="col-xs-3">';
            str += '		<select class="form-control" name="unit">';
            for (var i = 0; i < unit_list.length; i++) {
                val = unit_list[i];
                str += '<option value="' + val.unit_id + '"';
                if (i == 0) {
                    str += " selected";
                }
                str += '>'+ val.unit + '单元</option>';
            }
            str += '		</select>';
            str += '	</div>';
            str += '	<div class="col-xs-2">';
            str += '		<select class="form-control" name="room">';
            for (var i = 0; i < room_list.length; i++) {
                val = room_list[i];
                str += '<option value="' + val.outer_room_id + '"';
                if (i == 0) {
                    str += " selected";
                }
                str += '>'+ val.room + '</option>';
            }
            str += '		</select>';
            str += '	</div>';
            str += '	<div class="col-xs-1">';
            str += '    <a class="btn btn-danger btn-xs edit-del-room-btn" style="margin-top: 6px">';
            str += '	<i class="fa fa-minus" title=""></i> <span>删除房屋</span>';
            str += '</a>';
            str += '</div>';
            str += '</div>';
            this.addIndex++;
            return str;
        },

        get_room_ids: function () {
            var room_id_list = [];
            var self = this;
            self.flag = false;
            $(self.el).find('select[name=room]').each(function(){
                var room_id = $(this).val();
                if(room_id_list.indexOf(room_id) != -1){
                    console.info(room_id);
                    UI.showErrTip("同一个房间不允许绑定两次");
                    self.flag = true;
                    room_id_list = [];
                    return;
                }
                room_id_list.push(room_id);
            });
            return room_id_list;
        },



        events: {
            'change .card-new-type': function () {
                var card_type = $('.card-new-type').val();
                if (card_type == '1') {
                    $('.basedata-group').addClass('hide');
                    this.initData();
                } else {
                    $('.basedata-group').removeClass('hide');
                }
            },

            'change .card-new-group': function () {
                var self = this;
                $('.card-new-build').html('<option value="">楼栋</option>');
                $('.card-new-build').val("");
                $('.card-new-build').change();
                $.ajax({
                    url: '/basedata_api/Basedata_Build_Api/get_build_list_by_filter/1/',
                    type: 'POST',
                    data: {
                        project_id: $('#sProjectId').html(),
                        group_id: $('.card-new-group').val(),
                    },
                    dataType: 'json',
                    success: function (result) {
                        if (!!!result.data.build_list) {
                            return false;
                        }
                        var build_list = result.data.build_list;
                        self.build_list = build_list;
                        if (build_list.length > 0) {
                            if (build_list.length == 1) {
                                UI.createOption($('.card-new-build'), build_list, 'build_id', 'build_str', build_list[0]['build_id']);
                            } else {
                                UI.createOption($('.card-new-build'), build_list, 'build_id', 'build_str', "");
                            }
                            $('.card-new-build').change();
                        }
                    }
                });
            },

            'change .card-new-build': function () {
                var self = this;
                $('.card-new-unit').html('<option value="">单元</option>');
                $('.card-new-unit').val("");
                $('.card-new-unit').change();
                var build = $('.card-new-build').val();
                if (!build) {
                    return false;
                }
                $.ajax({
                    url: '/basedata_api/Basedata_Unit_Api/get_unit_list_by_filter/1/',
                    type: 'POST',
                    data: {
                        project_id: $('#sProjectId').html(),
                        group_id: $('.card-new-group').val(),
                        build_id: $('.card-new-build').val(),
                    },
                    dataType: 'json',
                    success: function (result) {
                        if (!!!result.data.unit_list) {
                            return false;
                        }
                        var unit_list = result.data.unit_list;
                        if (unit_list.length > 0) {
                            if (unit_list.length == 1) {
                                UI.createOption($('.card-new-unit'), unit_list, 'unit_id', 'unit_str', unit_list[0]['unit_id']);
                            } else {
                                UI.createOption($('.card-new-unit'), unit_list, 'unit_id', 'unit_str', "");
                            }
                            $('.card-new-unit').change();
                        }
                    }
                });
            },

            'change .card-new-unit': function () {
                var self = this;
                $('.card-new-room').html('<option value="">房间</option>');
                $('.card-new-room').val("");
                var unit = $('.card-new-unit').val();
                if (!unit) {
                    return false;
                }
                $.ajax({
                    url: '/basedata_api/Basedata_Apartment_Api/get_apartment_by_filter/1/',
                    type: 'POST',
                    data: {
                        project_id: $("#sProjectId").html(),
                        group_id: $('.card-new-group').val(),
                        build_id: $('.card-new-build').val(),
                        unit_id: $('.card-new-unit').val(),
                    },
                    dataType: 'json',
                    success: function (result) {
                        if (!!!result.data.apartment_list) {
                            return false;
                        }
                        var room_list = result.data.apartment_list;
                        if (room_list.length > 0) {
                            if (room_list.length == 1) {
                                UI.createOption($('.card-new-room'), room_list, 'outer_room_id', 'room', room_list[0]['outer_room_id']);
                            } else {
                                UI.createOption($('.card-new-room'), room_list, 'outer_room_id', 'room', "");
                            }
                        }
                    }
                });
            },

            'click .read-card-btn': function () {
                this.write_flag = false;
                window._qd_card_reader.invoke("read_card");
            },

            'click .write-card-btn': function () {
                var btn_html = $('.write-card-btn').html();
                if (btn_html === '重置') {
                    this.reset_card_info();
                    return;
                }
                this.write_flag = true;
                window._qd_card_reader.invoke("read_card");
            },

            'click .edit-add-room-btn': function() {
                if(this.addIndex>=8){
                    UI.showErrTip("不能超过9个房屋");
                    return false;
                }
                this.createRoom();
            },

            'change .add-room-list select':function(event) {
                var current_select = $(event.target);
                var select_name = current_select.attr('name');
                var select_value = current_select.val();
                var next_select = current_select.parent().next("div").find("select");
                var data = {
                    project_id: $('#sProjectId').html(),
                }
                var change_select_name = 'build';

                var url = '';
                if(select_name == 'group'){
                    next_select.html('<option value="">楼栋</option>');
                    url = '/basedata_api/Basedata_Build_Api/get_build_list_by_filter/1/';
                    data = $.extend(data, {
                        group_id: select_value
                    });
                }else if(select_name == 'build'){
                    next_select.html('<option value="">单元</option>');
                    url = '/basedata_api/Basedata_Unit_Api/get_unit_list_by_filter/1/';
                    data = $.extend(data, {
                        group_id: current_select.parent().siblings('div').find('select[name=group]').val(),
                        build_id: select_value
                    });
                    change_select_name = 'unit';
                }else if(select_name == 'unit'){
                    next_select.html('<option value="">房间</option>');
                    url = '/basedata_api/Basedata_Apartment_Api/get_apartment_by_filter/1/';
                    data = $.extend(data, {
                        group_id: current_select.parent().siblings('div').find('select[name="group"]').val(),
                        build_id: current_select.parent().siblings('div').find('select[name=build]').val(),
                        unit_id: select_value,
                    });
                    change_select_name = 'apartment';
                }
                next_select.val('');
                if(select_name=='room' || (!!! select_value && select_name != 'group')){return false}
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: data,
                    dataType: 'json',
                    success: function (result) {
                        var data_list = result.data[change_select_name+"_list"];
                        if (!!!data_list) {
                            return false;
                        }
                        var change_id = change_select_name+'_id';
                        var change_name = change_select_name+'_str';
                        if(change_select_name == 'apartment'){
                            change_id = 'outer_room_id';
                            change_name = 'room';
                        }
                        if (data_list.length > 0) {
                            if (data_list.length == 1) {
                                UI.createOption(next_select, data_list, change_id, change_name, data_list[0][change_id]);
                            } else {
                                UI.createOption(next_select, data_list, change_id, change_name, "");
                            }
                        }
                        next_select.change();
                    }
                });
            },

            'click .edit-del-room-btn':function(event) {
                this.addIndex -= 1;
                $(event.srcElement || event.target).closest('.select-room-list').remove();
            },
        }
    });