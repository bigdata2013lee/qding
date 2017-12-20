(function($) {

	var mm = qd.ns("views.project");

	/**
	 * 房屋列表
	 * @type {any}
	 */
	mm.AptmView = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/aptm/tpls/aptm.tpl',

		_query_pager: {
			page_no: 1,
			page_size: 12
		},

		initialize: function() {
			this._rooms = [];
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
			this.$el.find(".query_box>form").qd_phase_build_select();
			this.query_rooms();
		},

		events: {
			"click div.query_box .query_btn": function(evt) {
				var self = this;
				self._query_pager = { page_no: 1, page_size: 12 };
				self.query_rooms();
			},
			'click nav ul.pagination li': function(evt) {
				var page_no = $(evt.currentTarget).data('page_no') * 1;
				this._query_pager.page_no = page_no == 0 || isNaN(page_no) ? 1 : page_no;
				this.query_rooms();
			},
			'click td .residents_window_btn': function(evt) {
				var self = this,
					oid = $(evt.target).closest('tr').data('oid'),
					aptm = _.find(self._rooms, { id: oid });
				self.$el.find("#residents_window .modal-body").render_template(aptm);
				sessionStorage.master = $(evt.target).closest('tr').data('master');
				self.get_talk_connect_tel();
				self.list_aptm_residents(oid);
			},
			'click .deleteHouse': function(evt) {
				var self = this;
				var user_id = $(evt.target).closest('tr').data('oid');
				qd.rpc("qduser.QdUserApi.unbind_aptm_by_user_ids", params).success(function(result) {
					self.query_rooms();
				});
			},
			'click #residents_window button.bind_aptm_btn': function(evt) {
				var self = this;
				self.bind_aptm();
			},
			'click #residents_window a.unbind_aptm_btn': function(evt) {
				var self = this;
				var user_id = $(evt.target).closest('tr').data('oid');
				var params = qd.utils.serialize("#residents_window");
				self.unbind_aptm(user_id, params.aptm_id);
			},
			'click #residents_window a.admin_aptm_btn': function(evt) {
				var user_id = $(evt.target).closest('tr').data('oid'),
					params = qd.utils.serialize("#residents_window");
				this.transfer_master_role(user_id, params.aptm_id);
			},
			'click #residents_window button.bind_talk_connect_tel_btn': function(evt) {
				this.bind_talk_connect_tel();
			},
			'click #remove_connect_tel': function(evt) {
				this.bind_talk_connect_tel('remove');
			},
			"click .AddHouse_btn": function(evt) {
				this.add_room_for_wuye();
			}
		},

		query_rooms: function() {
			var self = this;
			var params = qd.utils.serialize(".query_box>form");
			params.phase_no = parseInt(params.phase_no * 1);
			params.building_no = parseInt(params.building_no * 1);
			qd.rpc("aptm.AptmQueryApi.query_rooms_for_wuye", $.extend({ pager: self._query_pager }, params))
				.success(function(result) {
					self.$el.find(".data_list_box").render_template(result);
					self._rooms = result.data.collection || [];
				});
		},

		bind_aptm: function() {
			var self = this,
				params = qd.utils.serialize("#residents_window");
			delete params.phone_number;
			qd.rpc("qduser.QdUserApi.bind_aptm_by_mobile", params).success(function(result) {
				self.list_aptm_residents(params.aptm_id);
			});

		},

		unbind_aptm: function(user_id, aptm_id) {
			var self = this;
			if(!window.confirm("你确定要解绑此用户吗？请谨慎操作!")) { return }
			var params = { user_ids: [user_id], aptm_id: aptm_id };
			qd.rpc("qduser.QdUserApi.unbind_aptm_by_user_ids", params).success(function(result) {
				self.list_aptm_residents(params.aptm_id);
			});
		},
		list_aptm_residents: function(aptm_id) {
			var self = this;
			qd.rpc("qduser.QdUserApi.get_aptm_residents", { aptm_id: aptm_id }).success(function(result) {
				self.$el.find("#residents_window div.part2").render_template(result);
			});
		},
		transfer_master_role: function(user_id, aptm_id) {
			var self = this;
			sessionStorage.master = user_id;
			qd.rpc("qduser.QdUserApi.wy_set_aptm_master", { user_id: user_id, aptm_id: aptm_id }).success(function() {
				self.list_aptm_residents(aptm_id);
				self.query_rooms();
			});
		},

		get_talk_connect_tel: function() {
			var self = this;
			var params = qd.utils.serialize("#residents_window");
			qd.rpc("qdtalk.TalkCommonApi.get_aptm_contact_phone", { aptm_id: params.aptm_id }).success(function(result) {
				//$("#talk_connect_tel").html(result.data.talk_contact_phone);
				self.$el.find(".connect_tel_box").render_template(result);
			})
		},

		bind_talk_connect_tel: function(action) {
			var self = this,
				params = qd.utils.serialize("#residents_window");
			delete params.mobile;
			if(action === "remove") { params.phone_number = ""; }
			qd.rpc("qdtalk.TalkCommonApi.set_aptm_contact_phone", params).success(function() {
				self.list_aptm_residents(params.aptm_id);
				self.get_talk_connect_tel();
			});
		},
		_v: function(params) {
			var rules = {
				"building_no": "required",
				"unit": {
					method: function(val) {
						val = parseInt(val);
						console.log(val)
						if(val >= 200) {
							return false;
						} else {
							return true;
						}
					},
					rule: "function"
				}
			};
			var messages = {
				"building_id": "请输入楼栋",
				"unit": "单元数>=200"
			};
			var v = new qd.utils.Validator(rules, messages);
			return v.validate(params);

		},
		add_room_for_wuye: function() {
			var params = qd.utils.serialize('div.submit_box');
			var self = this;
			delete params.phase_id;
			params.phase_no = parseInt(params.phase_no * 1);
			params.building_no = parseInt(params.building_no * 1);
			params.floor_no = parseInt(params.floor_no * 1);
			params.unit_no = parseInt(params.unit_no * 1);
			params.room_no = parseInt(params.room_no * 1)
			if(!this._v(params)) return;
			for(var key in params) {
				if(key == "unit" || key == "room" || key == "floor") { params[key] = params[key] * 1; }
			}
			qd.rpc("aptm.AptmManageApi.wy_add_room", params).success(function(result) {
				if(result.err != 0) {
					return;
				}
				$('#AddHouse_input').get(0).reset();
				$('#AddHouse').modal('hide');
				self.query_rooms();
			});
		}

	});

	/**
	 * 楼栋(期)
	 * @type {any}
	 */
	mm.PhaseView = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/aptm/tpls/phase.tpl',

		_query_pager: {
			page_no: 1,
			page_size: 12
		},

		initialize: function() {
			this._rooms = [];
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
			this.list_phases();
		},

		events: {},

		list_phases: function() {
			var self = this;
			qd.rpc("aptm.AptmQueryApi.list_phases", { project_id: select_project_id }).success(function(result) {
				self.$el.find(".data_list_box").render_template(result);
				self.$el.find(".data_list_box>ul>li").each(function() {
					self.list_buildings($(this));
				})
			});

		},

		list_buildings: function(phase_li) {
			var phase_id = phase_li.data("phase_id");
			qd.rpc("aptm.AptmQueryApi.list_buildings", { phase_id: phase_id }).success(function(result) {
				phase_li.find(".data_body").render_template(result);
			});

		}
	});

	/**
	 * 添加房屋
	 * @type {any}
	 */
	//		mm.AddAptmView = Backbone.View.extend({
	//			className: 'view_box',
	//			_tpl: '/static/aptm/tpls/add_aptm.tpl',
	//	
	//			_query_pager: {},
	//	
	//			initialize: function() {
	//				qd.load_view_tpls(this._tpl);
	//				$(this.el).render_template({}, 'view');
	//				$(app_router.content).html(this.el);
	//				this.$el.find(".submit_box>form").qd_phase_build_select();
	//			},
	//	
	//			events: {
	//				"click div.submit_box .submit_btn": function(evt) {
	//					this.add_room_for_wuye();
	//				}
	//	
	//			},
	//			_v: function(params) {
	//				var rules = {
	//					"building_no": "required",
	//					"unit": {
	//						method: function(val) {
	//							val = parseInt(val);
	//							console.log(val)
	//							if(val >= 200) {
	//								return false;
	//							} else {
	//								return true;
	//							}
	//						},
	//						rule: "function"
	//					}
	//				};
	//				var messages = {
	//					"building_id": "请输入楼栋",
	//					"unit": "单元数>=200"
	//				};
	//				var v = new qd.utils.Validator(rules, messages);
	//				return v.validate(params);
	//	
	//			},
	//			add_room_for_wuye: function() {
	//				var params = qd.utils.serialize('div.submit_box');
	//				delete params.phase_id;
	//				params.phase_no = parseInt(params.phase_no * 1);
	//				params.building_no = parseInt(params.building_no * 1);
	//				params.floor = parseInt(params.floor * 1);
	//				if(!this._v(params)) return;
	//				for(var key in params) {
	//					if(key == "unit" || key == "room" || key == "floor") { params[key] = params[key] * 1; }
	//				}
	//				qd.rpc("aptm.AptmManageApi.wy_add_room", params);
	//			}
	//	
	//		});

	/**
	 * 房屋绑定审核
	 * @type {any}
	 */
	mm.AptmBindReviewedView = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/aptm/tpls/bind_reviewed.tpl',

		_query_pager: {
			page_no: 1,
			page_size: 10
		},

		initialize: function() {
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
			this.$el.find(".query_box>form").qd_phase_build_select();
			this.query_reviews();
			$("#notice-icon").hide();
		},

		events: {
			'click nav ul.pagination li': function(evt) {
				var page_no = $(evt.currentTarget).data('page_no') * 1;
				this._query_pager.page_no = page_no == 0 || isNaN(page_no) ? 1 : page_no;
				this.query_reviews();
			},

			"click div.query_box .query_btn": function(evt) {
				this.query_reviews();
			},

			"click a.a-modal": function(evt) {
				$("#user_notice").html(evt.target.getAttribute("data-user-notice"));
				$("#wy_notice").html(evt.target.getAttribute("data-wy-notice"));
				$('#log_window').modal();
			},

			"click a.pass-btn": function(evt) {
				if(!window.confirm('你确认要通过该申请？')) { return; }
				var oid = $(evt.target).closest("tr").data("oid");
				this.pass_review(oid);
			},

			"click a.reject-btn": function(evt) {
				$('#reject_window').modal();
				sessionStorage.oid = $(evt.target).closest("tr").data("oid");
			},

			"click button.reject-submit": function(evt) {
				this.review_reject_submit();
			},

			/*"change select[name=status]": function (evt) {
			    this.query_reviews();
			}*/
		},

		query_reviews: function() {
			var self = this,
				params = qd.utils.serialize(".query_box>form");
			qd.rpc("application.ApplicationApi.wy_query_aptm_applications", $.extend({ pager: self._query_pager }, params)).success(function(result) {
				self.$el.find(".data_list_box").render_template(result);
			});
		},

		pass_review: function(oid) {
			var self = this,
				params = {};
			params.application_id = oid;
			params.status = "pass";
			params.wy_notice = "";
			qd.rpc("application.ApplicationApi.wy_check_atpm_application", params).success(function(result) {
				self.query_reviews();
			});
		},

		review_reject_submit: function() {
			if(!$("#wy_notice_txt").val()) {
				qd.notify.error("请输入审核原因");
				return;
			}

			var self = this,
				params = {};
			params.application_id = sessionStorage.oid;
			params.status = "reject";
			params.wy_notice = $("#wy_notice_txt").val();

			qd.rpc("application.ApplicationApi.wy_check_atpm_application", params).success(function(result) {
				self.query_reviews();
				$('#reject_window').modal("hide");
			});
		}

	});

	/**
	 * 房屋列表模板下载
	 * @type {any}
	 */
	mm.AptmTplsView = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/aptm/tpls/help.tpl',

		initialize: function() {
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
		}
	});

})(jQuery);