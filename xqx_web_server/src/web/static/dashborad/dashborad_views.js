(function($) {

	var init_datetimepicker = function() {
		setTimeout(function() {
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
	var init_datetimepicker2 = function() {
		setTimeout(function() {
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
	var mm = qd.ns("views.dashborad");

	mm.DashboradView = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/dashborad/tpls/dashborad.tpl',

		_query: {},

		initialize: function() {
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
			this.query_alarm_list();
			init_datetimepicker2();
			init_datetimepicker();
		},
		events: {
			'click #add_resident_card_window .sumbit_btn': function(evt) {
				this.register_resident_card();
			},
			'click #add_manager_card_window .sumbit_btn': function(evt) {
				this.register_manager_card();
			},
			'click #add_worker_card_window .sumbit_btn': function(evt) {
				this.register_worker_card();
			},
		},
		query_alarm_list: function() {
			var self = this;

			//报警统计(最近3天)
			qd.rpc("statistic.StatisticApi.stt_alarm_categorys", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".alarm_list_box").render_template(result);
			});

			//最近报警记录
			qd.rpc("statistic.StatisticApi.get_last_alarms", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".recent_alarm_list_box").render_template(result);
			});

			//设备状态
			qd.rpc("statistic.StatisticApi.stt_all_device_onlines", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".device_status_list_box").render_template(result);
			});

			//近期离线设备
			qd.rpc("statistic.StatisticApi.get_last_offline_gates", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".gates_list_box").render_template(result);
			});

			qd.rpc("statistic.StatisticApi.get_last_offline_agws", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".agws_list_box").render_template(result);
			});

			qd.rpc("statistic.StatisticApi.get_last_offline_aios", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".aios_list_box").render_template(result);
			});
		},
		register_resident_card: function() {
			var self = this;
			var params = {};
			var _params = qd.utils.serialize("#add_resident_card_window");

			//验证
			for(var key_name in _params) {
				if(key_name in { 'card_no': 1, 'expiry_date': 1 }) { continue }
				_params[key_name] = _params[key_name] * 1;
				if(!_params[key_name]) {
					qd.notify.error("房号信息错误");
					return;
				}
			}

			params.apm_fuuid = qd.utils.formatStr("{0}-{1}-{2}-{3}-{4}", _params.phase, _params.build, _params.unit, _params.floor, _params.room);
			params.card_no = _params.card_no + '';
			params.expiry_date = _params.expiry_date;

			qd.rpc("card.AccessCardApi.register_resident_card", params).success(function(result) {
				if(result.err == 0) {
					$('#add_resident_card_window').modal('hide');
					self.list_resident_cards();

					var room = $("#add_resident_card_window input[name=room]").val();
					$("#add_resident_card_window input[name=room]").val((room * 1) + 1);
					$("#add_resident_card_window input[name=card_no]").val("");
				}
			});
		},

		register_manager_card: function() {
			var self = this;
			var params = qd.utils.serialize("#add_manager_card_window");
			params.card_type = 'manager';
			qd.rpc("card.AccessCardApi.register_wuye_work_card", params).success(function(result) {
				if(result.err == 0) {
					$('#add_manager_card_window').modal('hide');
				}
			});
		},

		register_worker_card: function() {
			var self = this;
			var params = qd.utils.serialize("#add_worker_card_window");
			params.card_type = 'worker';
			qd.rpc("card.AccessCardApi.register_wuye_work_card", params).success(function(result) {
				if(result.err == 0) {
					$('#add_worker_card_window').modal('hide');
				}
			});
		},

	});

})(jQuery);