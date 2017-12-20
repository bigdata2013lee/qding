(function($) {

    var mm = qd.ns("views.maintain");

    var init_datetimepicker =function () {
        setTimeout(function(){
            $(".up.has-feedback.date").datetimepicker({
                format: "yyyy/mm/dd",
                autoclose: true,
                todayBtn: true,
                pickerPosition: "top-left" || pickerPosition,
                minView: 2,
                language: 'zh-CN'
            });

        }, 2);
    };
    var init_datetimepicker2 =function () {
        setTimeout(function(){
            $(".down.has-feedback.date").datetimepicker({
                format: "yyyy/mm/dd",
                autoclose: true,
                todayBtn: true,
                pickerPosition: "bottom-left",
                minView: 2,
                language: 'zh-CN'
            });

        }, 2);
    };

    mm.CardView = Backbone.View.extend({
        className: 'view_box',
        token: true,
        _tpl:'/static/maintain/tpls/maintain_card.tpl',

        _query:{
            page_no: 1,
            sort_type:"-updated_at"
        },
        initialize: function () {
            qd.load_view_tpls(this._tpl);
            $(this.el).render_template({}, 'view');
            $(app_router.content).html(this.el);
            this.list_resident_cards();
            init_datetimepicker();
            init_datetimepicker2();

        },

        events: {
            'click #add_resident_card_window .sumbit_btn':function (evt) {
                this.register_resident_card();
            },
            'click #add_manager_card_window .sumbit_btn':function (evt) {
                this.register_manager_card();
            },
            'click #add_worker_card_window .sumbit_btn':function (evt) {
                this.register_worker_card();
            },
            'click #import_cards_window .sumbit_btn':function (evt) {
                this.import_cards();
            },

            'click a[name=unregister_card]':function (evt) {
                var tr  = $(evt.target).closest('tr');
                var oid  = tr.data('oid');
                this.unregister_card(oid, tr);
            },
            'click nav ul.pagination li':function (evt) {
                var page_no = $(evt.currentTarget).data('page_no') * 1;
                if(page_no == 0 || isNaN(page_no)){page_no = 1}
                this._query.page_no = page_no;
                this.query();
            },

            'click .query_box .query_btn': function (evt) {
                var self = this;
                self._query.page_no = 1;
                self.query();
            },
            'change .query_box select[name=card_type]':function (evt) {
                var self = this;
                var card_type = this.$el.find('.query_box select[name=card_type]').val();
                if(card_type in  {'':1,'manager':1, 'worker':1}){
                    $(".query_box  .form-group.apm_c").hide();
                    $(".query_box  .form-group.like_input").show();
                }
                else if(card_type == 'resident'){
                    $(".query_box  .form-group.apm_c").show();
                    $(".query_box  .form-group.like_input").hide();
                }
            },
            'click ul.sort_type .option>a':function (evt) {
                var self = this;
                $('ul.sort_type .option>a>i').removeClass('glyphicon-ok');
                var sort_type = $(evt.currentTarget).data("sort_type");
                $(evt.currentTarget).find('i').addClass('glyphicon-ok');
                self._query.sort_type = sort_type;
            },
            'change .form-group input[name=myfiles]': function (evt) {

            }
        },

        query:function () {
            var self = this;
            var card_type = this.$el.find('.query_box select[name=card_type]').val();
            if(card_type in  {'':1, 'manager':1, 'worker':1}){
                var card_no_like = this.$el.find('.query_box input[name=card_no_like]').val();
                var owner_name_like = this.$el.find('.query_box input[name=owner_name_like]').val();
                self.list_cards(card_type, card_no_like, owner_name_like);
            }
            else if(card_type == 'resident'){
                self.list_resident_cards();
            }
        },

        list_resident_cards:function () {
            var self =  this;
            var apartment_uuid_like = "";
            var _params = qd.utils.serialize(".query_box .form-group.apm_c");
            for(var key_name in  _params){
                _params[key_name] = _params[key_name] * 1;
            }
            apartment_uuid_like = qd.utils.formatStr('{0}-{1}-{2}-{3}-{4}', _params.phase, _params.build, _params.unit, _params.floor, _params.room);

            var params={aptm_fuuid_like:apartment_uuid_like, pager: { page_no:  self._query.page_no }};

            qd.rpc("card.AccessCardApi.list_resident_cards", params).success(function (result) {
                qd.render_template("data_list", result, self.$el.find('.data_list_div'));
            });
        },
        list_cards:function (card_type, card_no_like, owner_name_like) {
            var self = this;
            var params = {
                card_type:card_type, card_no_like:card_no_like, owner_name_like:owner_name_like,
                pager: { page_no:  self._query.page_no }
            };

            qd.utils.trimObj(params);
            qd.rpc("card.AccessCardApi.list_cards", params).success(function (result) {
                qd.render_template("data_list", result, self.$el.find('.data_list_div'));
            });
        },
        unregister_card:function(oid, tr){
            if(!window.confirm("你确定要删除/注销此卡号？")){return;}
            qd.rpc("card.AccessCardApi.unregister_card", {card_id:oid}).success(function (result) {
                if(result.err == 0){
                    $(tr).remove();
                }
            })
        },
        register_resident_card:function () {
            var self = this;
            var params = {};
            var _params = qd.utils.serialize("#add_resident_card_window");

            //验证
            for(var key_name in _params){
                if(key_name in {'card_no':1, 'expiry_date':1}){continue}
                _params[key_name] = _params[key_name] * 1;
                if(!_params[key_name]){
                    qd.notify.error("房号信息错误");
                    return;
                }
            }

            params.apm_fuuid =  qd.utils.formatStr("{0}-{1}-{2}-{3}-{4}", _params.phase, _params.build, _params.unit, _params.floor, _params.room);
            params.card_no = _params.card_no + '';
            params.expiry_date = _params.expiry_date;

            qd.rpc("card.AccessCardApi.register_resident_card", params).success(function (result) {
                if(result.err==0){
                    //$('#add_resident_card_window').modal('hide');
                    self.list_resident_cards();

                    var room = $("#add_resident_card_window input[name=room]").val();
                    $("#add_resident_card_window input[name=room]").val((room * 1) + 1);
                    $("#add_resident_card_window input[name=card_no]").val("");
                }
            });
        },

        register_manager_card:function () {
            var self = this;
            var params = qd.utils.serialize("#add_manager_card_window");
            params.card_type = 'manager';
            qd.rpc("card.AccessCardApi.register_wuye_work_card", params).success(function (result) {
                if(result.err==0){
                    $('#add_manager_card_window').modal('hide');
                }
            });
        },

        register_worker_card:function () {
            var self = this;
            var params = qd.utils.serialize("#add_worker_card_window");
            params.card_type = 'worker';
            qd.rpc("card.AccessCardApi.register_wuye_work_card", params).success(function (result) {
                if(result.err==0){
                    $('#add_worker_card_window').modal('hide');
                }
            });
        },
        import_cards:function () {
            var self = this;
            if(self.token){
                self.token = false;
                var oProgress = $('.progress').show();
                $('#import_cards_window form:first').ajaxSubmit({
                    url: '/remote/card.ImportExportCardApi.import_cards/',
                    type: 'POST',
                    dataType: 'json',
                    beforeSubmit: function(form_data, jq_form, options) {

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
                            $('#import_cards_window form:first')[0].reset();
                            $('#import_cards_window').modal('hide');
                        }
                    },
                    complete: function(xhr, ts) {
                        oProgress.hide();
                        self.token = true;
                        $('#qd_cover_layer').hide();
                        $('#percent').css('width', '0');
                    }
                });
            }
        }
    });

})(jQuery);