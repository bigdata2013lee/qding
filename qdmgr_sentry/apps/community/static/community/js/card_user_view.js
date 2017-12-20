var card_user_view = Backbone.View.extend({
    className: 'card_user_view',
    page_no: 1,
    page_size:30,
    select_list_dict: {
        card_type_selected:"", card_status_selected:"",
        group_list:[], group_selected:"",
        build_list:[], build_selected:"",
        unit_list:[], unit_selected:"",
        room_list:[], room_selected:""
    },

    _clear:function(name){
        var self = this;
        self.select_list_dict[name+'_list'] = [];
        self.select_list_dict[name+'_selected'] = "";
        return self;
    },

    _list:function(name, alist){
        var self = this;
        self.select_list_dict[name+'_list'] = alist;
        return self;
    },
    /**
     * getter/setter  of  select_list_dict.xxx_selected
     * @param name
     * @param val
     */
    _sld:function(name, val){
        var self = this;
        if(val === undefined){return self.select_list_dict[name+'_selected']}
        self.select_list_dict[name+'_selected'] = val;
        return self;
    },
    _render_search_box:function(){
        var self = this;
        $(".card-search-box").render_template(self.select_list_dict);
        return self;
    },
    _get_area_info: function () {
        return {
            province: $("#sProvince").html(),
            city: $("#sCity").html(),
            project: $("#sCommunity").html()
        }
    },
    initialize:function() {
        qd.load_view_tpls(CONST.static_url+'community/ejs/card_user_manage.tpl');
        $(this.el).render_template({},"view");
        this.getGroupList();
        this.getList();
    },

    loadData:function() {
        this.getGroupList();
        this.getList();
    },


    getGroupList: function () {
        var self = this;
        self._clear("build")._clear("unit")._clear("room");
        $.ajax({
            url: '/basedata_api/Basedata_Group_Api/get_group_list/1/',
            type: 'POST',
            data: $.extend({}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                self._list('group',result.data.group_list)._render_search_box();
                self.getBuildList();

            }
        });
    },

    getBuildList: function () {
        var self = this;
        self._clear("unit")._clear("room");
        $.ajax({
            url: '/basedata_api/Basedata_Build_Api/get_build_list/1/',
            type: 'POST',
            data: $.extend({group: self._sld('group')}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                self._list('build', result.data.build_list)._render_search_box();
                if(self._sld('build') != ""){self.getUnitList()}
            }
        });
    },
    getUnitList:function(){
        var self = this;
        self._clear("room");
        $.ajax({
            url: '/basedata_api/Basedata_Unit_Api/get_unit_list/1/',
            type: 'POST',
            data: $.extend({group: self._sld('group'), build: self._sld('build')}, self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                self._list('unit', result.data.unit_list)._render_search_box();
                if(self._sld('unit') != ""){self.getRoomList()}
            }
        });
    },
    getRoomList:function(){
        var self = this;
        $.ajax({
            url: '/basedata_api/Basedata_Apartment_Api/get_room_list/1/',
            type: 'POST',
            data: $.extend({group: self._sld('group'),build: self._sld('build'),unit: self._sld('unit')},self._get_area_info()),
            dataType: 'json',
            success: function (result) {
                self._list('room',result.data.room_list)._render_search_box();
            }
        });
    },

    getList: function (pageIndex) {
        if (typeof pageIndex == "undefined") {
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;
        $.ajax({
            url: '/brake_api/Brake_Card_Api/get_card_by_filter/1/',
            type: 'POST',
            data: {
                page_no: _this.page_no,
                page_size: _this.page_size,
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                project: $("#sCommunity").html(),
                group: $('.search-card-group').val(),
                build: $('.search-card-build').val(),
                unit: $('.search-card-unit').val(),
                room: $('.search-card-room').val(),
                card_type: $('.search-card-type').val(),
                status: $('.search-card-status').val(),
            },
            dataType: 'json',
            success: function (result) {
                if (result.data.flag == "Y") {
                    _this.$el.find('.list-block').render_template({list: result.data.card_list});
                    var str = '<button type="button" class="btn btn-info">总数：' + result.data.pagination.total_count + '</button>';
                    $(".brake_card_count").html(str);
                    if (!_this.page_inited) {
                        _this.initPager(result.data.pagination.total_count);
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

    events:{
        'change .search-card-group': function (evt) {
            var self = this;
            self._sld('group',$(evt.target).val()).getBuildList();
        },

        'change .search-card-build': function (evt) {
            var self = this;
            self._sld('build',$(evt.target).val()).getUnitList();
        },

        'change .search-card-unit': function (evt) {
            var self = this;
            self._sld('unit',$(evt.target).val()).getRoomList();
        },

        'change .search-card-room':function (evt){
            var self = this;
            self._sld('room',$(evt.target).val());
        },

        'change .search-card-type': function(evt) {
            var self = this;
            self._sld('card_type',$(evt.target).val());
        },

        'change .search-card-status': function(evt) {
            var self = this;
            self._sld('card_status',$(evt.target).val());
        },

        'change .operate-box select':function(evt){
            this.getList();
        },

        'click .remove-card-btn': function (event){
            if (!confirm('确定要注销吗？')) return true;

            var tr = $(event.target).closest("tr");
            var card_no = tr.data('card-no');
            var self = this;

            $.ajax({
                url: '/brake_api/Brake_Card_Api/delete_card/',
                type: 'POST',
                data: {
                    card_no: card_no,
                },

                dataType: 'json',
                success: function(result){
                    if (result.data.flag == 'Y'){
                        self.getList();
                    }
                }
            });
        },

        'click .edit-card-btn':function(event) {
            var _this = $(event.srcElement || event.target);
            var item=_this.parents("tr.card-item");
            var id = item.data("card-id");
            $.ajax({
                url: '/brake_api/Brake_Card_Api/get_card_by_filter/',
                type: 'POST',
                data: {
                    card_id: id,
                },
                dataType: 'json',
                success: function(result){
                    var card_list = result.data.card_list;
                    if(card_list.length != 1){
                        return false;
                    }
                    var card_obj = card_list[0];
                    $("#edit-card-modal .modal-body").render_template(card_obj);
                }
            });
            $('#edit-card-modal').modal('show');
        },

        'click .submit-card-btn': function() {
            var id = $('#edit-card-modal input[name="card-id"]').val();
            var phone = $('#edit-card-modal input[name="card-phone"]').val();
            var status = $('#edit-card-modal select[name="card-status"]').val();
            var name = $('#edit-card-modal input[name="card-name"]').val();
            var self = this;
            if(!!!id){
                UI.showErrTip("未能正确获取id，请联系管理员");
                return false;
            }
            if(phone!="" && !/^1\d{10}$/.test(phone)){
                UI.showErrTip("请填写正确的手机号码");
                return false;
            }
            if(name !="" && name.length > 10){
                UI.showErrTip("名字不能超过10个字");
                return false;
            }
            $.ajax({
                url:'/brake_api/Brake_Card_Api/modify_card/1/',
                type: 'POST',
                data:{
                    card_id: id,
                    phone: phone,
                    name: name,
                    status: status,
                },
                dataType: 'json',
                success: function(result){
                    if (result.data.flag == 'N'){
                        UI.showErrTip(result.msg);
                        return false;
                    }
                    $('#edit-card-modal').modal('hide');
                    self.getList();
                }
            });
        },
    }
});