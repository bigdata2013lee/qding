var brake_device_binding_view = Backbone.View.extend({
    template: versionify(CONST.static_url + 'community/ejs/device_binding_block.html'),
    getBrakeListTimer: 0,
    brakeMacList: [],

    initialize: function () {
        $(this.el).html(new EJS({url: this.template}).render({}));
        var self = this;
        setTimeout(function () {
            self.loadData()
        }, 10);
    },

    loadData: function () {
        this.getGroupList();
    },

    getList: function () {
        var _this = this;
        _this.brakeMacList = [];
        $.ajax({
            url: '/brake_api/Brake_Machine_Api/get_brake_machine_by_filter/1/',
            type: 'POST',
            data: {
                brake_type: $(".search-brake-type").val(),
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $('.search-brake-group').val(),
                build: $('.search-brake-build').val(),
                unit: $('.search-brake-unit').val(),
                mac: $('.search-brake-mac').val(),
            },
            dataType: 'json',
            success: function (result) {
                for (i = 0; i < result.data.brake_machine_list.length; i++) {
                    _this.brakeMacList.push(result.data.brake_machine_list[i].mac);
                }
                var ejs_html = new EJS({url: CONST.static_url + 'community/ejs/device_binding_list_block.html'})
                    .render({list: result.data.brake_machine_list});
                $(_this.el).find('.brake-binding-list').html(ejs_html);
            }
        });
    },

    getGroupList: function () {
        $('.search-brake-group').html('<option value="">--  组团  --</option>');
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
                if (group_list.length > 0) {
                    UI.createSimpleOption($('.search-brake-group'), group_list);
                }
                $('.search-brake-group').change();
            }
        });
    },

    events: {
        'change .search-brake-type': function() {
            $('.search-brake-group').change();
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
            this.getList();
        },

        'keyup .search-brake-mac': function () {
            var self = this;
            window.clearTimeout(self.getBrakeListTimer);
            self.getBrakeListTimer = setTimeout(function () {
                self.getList();
            }, 400);
        },

        'click .search-btn':function(){
            this.getList();
        },

        'click .binding-btn': function () {
            var phone = $('.binding-brake-phone').val();
            if (!qd.utils.isVaildPhone(phone)) {
                UI.showErrTip('请填写正确的手机号');
                return false;
            }
            var self = this;
            $.ajax({
                url: '/basedata_api/Basedata_Bj_App_User_Api/set_app_user_can_open_door_list/1/',
                type: 'POST',
                data: {
                    brake_mac_list: JSON.stringify(self.brakeMacList),
                    phone:  phone,
                },
                dataType: 'json',
                success: function (result) {
                    if(result.data.flag == 'N'){
                        UI.showErrTip(result.msg);
                    }else{
                        UI.showSucTip("绑定成功，快去开门吧 O(∩_∩)O~");
                    }
                }
            });
        },
    }
});