(function($) {
	var mm = qd.ns("views.project");
	var init_datetimepicker = function() {
		$(".startTime").datetimepicker({
			format: "yyyy/mm/dd",
			autoclose: true,
			todayBtn: true,
			pickerPosition: "top-left" || pickerPosition,
			minView: 2,
			language: 'zh-CN'
		});
	};
	var init_datetimepicker2 = function() {
		$(".endTime").datetimepicker({
			format: "yyyy/mm/dd",
			autoclose: true,
			todayBtn: true,
			pickerPosition: "top-left" || pickerPosition,
			minView: 2,
			language: 'zh-CN'
		});
	};
	mm.Advertisement = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/qd/Advertisement/tpls/Advertisement.tpl',
		token: true,
		_query_pager: {},
		initialize: function() {
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
			this.query_project_list();
			init_datetimepicker();
			init_datetimepicker2();
			dataOid: "";
			chk_list: [];
			eidtchk_list: [];
		},
		events: {
			"click div.submit_box .submit_btn": function(evt) {
				this.submitbut();
			},
			'click .tree': function() {
				var self = this;
				var chk_value = [];
				$('.pcityApi ul ul li input:checked').each(function() {
					chk_value.push($(this).val());
				});
				console.log(chk_value);
				if(chk_value.length == 0) {
					qd.notify.error('您还没有选择任何范围！')
				} else {
					self.chk_list = chk_value
					$('#PCityApi').modal('hide')
				}
			},
			'click .editTree': function() {
				var self = this;
				var chk_value = [];
				$('.editpcityApi ul ul li input:checked').each(function() {
					chk_value.push($(this).val());
				});
				if(chk_value.length == 0) {
					qd.notify.error('您还没有选择任何范围！')
				} else {
					self.eidtchk_list = chk_value
					$('#editPCityApi').modal('hide')
				}
			},
			'click .remove_project': function(evt) {
				this.submit_remvoe_project($(evt.target).closest("tr").data('oid'));
			},
			'click button.sumbit_btn': function() {
				this.submit()
			},
			'click a.modify_modal': function(evt) {
				var self = this;
				self.dataOid = $(evt.target).closest("tr").data('oid')
				this.Echo(self.dataOid);
			},
			'click button.edit_but': function() {
				this.edit_submit();
			},
			'click .add_PCityApi': function() {
				this.pcityApi();
			},
			'click .edit_PCityApi': function() {
				this.EditpcityApi();
			}
		},
		submit: function() {
			var self = this;
			var list = {};
			params = qd.utils.serialize(self.$el.find('#Advertesment_list'));
			params.weight = parseInt(params.weight);
			params.project_ids = self.chk_list;
			console.log(params)
			if(params.adv_name == "") {
				qd.notify.error('请填写广告标题')
				return;
			}
			if(params.start_date == "" && params.end_data == "") {
				qd.notify.error('请填写正确时间')
				return;
			}
			if(params.company_name == "") {
				qd.notify.error('请填写所属公司')
				return;
			}
			if(params.project_ids == undefined) {
				qd.notify.error('请添加广告范围')
				return;
			}
			$('#Advertesment_list').ajaxSubmit({
				url: '/remote/advertising.AdvApi.mgr_submit_adv/',
				type: 'POST',
				dataType: 'json',
				beforeSubmit: function(form_data, jq_form, options) {
					form_data.push({ name: "_params", value: JSON.stringify(params) });
				},
				uploadProgress: function(event, position, total, percent) {
					$('#percent').css('width', ' ' + percent + '%').children("span").html(' ' + percent + '%');
				},
				success: function(result) {
					if(result.err != 0) {
						qd.notify.error(result.msg);
						return;
					}
					qd.notify.info(result.msg);
					$('#Advertesment_list').get(0).reset();
					$('#EstablishAdvertList').modal('hide');
					self.query_project_list();
					self.query_project_listself.dataOidself.dataOid();
				},
				complete: function(xhr, ts) {
					oProgress.hide();
					$('#percent').css('width', '0');
					self.token = true;
				}
			});
		},
		query_project_list: function() {
			var self = this,
				params = qd.utils.serialize('div.query_box');
			qd.rpc("advertising.AdvApi.mgr_list_advs", $.extend({ pager: self._query_pager }, params)).success(function(result) {
				self.$el.find(".data_list_box").render_template(result);
			});
		},
		submit_remvoe_project: function(pid) {
			if(!window.confirm("你确定要删除此条广告？")) { return; }
			var self = this;
			qd.rpc("advertising.AdvApi.remove_adv", { adv_id: pid }).success(function(result) {
				self.query_project_list();
			});
		},
		edit_submit: function() {
			var self = this;
			params = qd.utils.serialize('#edit_list');
			params.project_ids = self.eidtchk_list;
			params.weight = parseInt(params.weight);
			console.log(params)
			qd.rpc("advertising.AdvApi.mgr_edit_adv", $.extend({ adv_id: self.dataOid }, params)).success(function(result) {
				if(result.err == 0) {
					$('#edit_list').get(0).reset();
					$('#EditStatus').modal('hide');
					setTimeout(function() {
						self.query_project_list();
					}, 200);
				}
			});
		},
		pcityApi: function() {
			$("#pcityApi_list").html("");
			qd.rpc("pcity.PCityApi.tree_all_city_proejcts", {}).success(function(result) {
				qd.qd_layui(result, $("#pcityApi_list"));
			});
		},
		EditpcityApi: function() {
			$("#editpcityApi_list").html("");
			var self = this;
			qd.rpc("pcity.PCityApi.tree_all_city_proejcts", {}).success(function(result) {
				var id_layui = $("#editpcityApi_list");
				qd.qd_layui(result, id_layui);
				qd.rpc("advertising.AdvApi.get_adv", { adv_id: self.dataOid }).success(function(result) {
					for(var c = 0; c < result.data.adv.projects.length; c++) {
						for(var d = 0; d < $('.editpcityApi ul ul li input').length; d++) {
							if($('.editpcityApi ul ul li input')[d].value == result.data.adv.projects[c]) {
								$($('.editpcityApi ul ul li input')[d]).attr("checked", "checked");
							}
						}
					}
				});
			});
		},
		Echo: function(oid) {
			qd.rpc("advertising.AdvApi.get_adv", { adv_id: oid }).success(function(result) {
				$(".startTime").val(new Date(result.data.adv.start_at).format('yyyy/MM/dd'))
				$(".endTime").val(new Date(result.data.adv.end_at).format('yyyy/MM/dd'))
				$(".edit_weight").val(result.data.adv.weight)
			});
		}
	});
})(jQuery);