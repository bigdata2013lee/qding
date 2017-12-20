(function($) {
	var init_datetimepicker = function() {
		var date = new Date;
		$(".startTime").datetimepicker({
			format: "yyyy/mm/dd hh:00",
			autoclose: true,
			todayBtn: true,
			pickerPosition: "top-left" || pickerPosition,
			minView: 1,
			language: 'zh-CN',
			startDate: new Date(date.setHours(date.getHours() + 1)).format('yyyy-MM-dd hh'),
			endDate: new Date((new Date()/1000+86400)*1000)
		});
	};
	var mm = qd.ns("views.upgrade");

	mm.MainView = Backbone.View.extend({
		className: 'view_box',
		token: true,
		_ejs: '/static/upgrade/tpls/index_block.ejs',
		_tpl: '/static/upgrade/tpls/release.tpl',
		initialize: function() {
			var self = this;
			this.cache_collection = [];
			qd.load_view_tpls(self._tpl);
			var ejs_html = new EJS({ url: this._ejs }).render({});
			$(this.el).html(ejs_html);
			$(app_router.content).html(this.el);
			init_datetimepicker();
			this.page_info = { page_no: 1, page_size: 10 };
			this.listReleases();
		},

		events: {
			'click .qd_query_params .query_btn': function(evt) {
				this.page_info.page_no = 1;
				this.listReleases();
			},
			'click .data_list_div ul.pagination>li': function(evt) {
				var page_no = $(evt.currentTarget).data('page_no');
				if(!page_no) { return; }
				this.page_info.page_no = page_no;
				this.listReleases();
			},
			'click .data_list_div a[name=rm_btn]': function(evt) {
				this.remove_release2($(evt.target).closest('tr'));
			},
			'click .submit-version-release-btn': function(evt) {
				this.submit();
			},
			'click .deletePackage': function(evt) {
				var self = this;
				if(!window.confirm("你确定要停用此版本?")) { return }
				var oid = $(evt.target).closest('tr').data('oid')
				qd.rpc("upgrade.ComponentUpgradeApi.remove_verison", { ver_id: oid }).success(function(result) {
					if(result.err == 0) {
						self.listReleases();
					}
				});
			},
			'click .immediately': function() {
				$(".delay").css('display', 'block');
				$(".immediately_div").css('display', 'none');
			},
			'click .Release': function() {
				$(".delay").css('display', 'none');
				$(".immediately_div").css('display', 'block');
				var state = $(".immediately").attr('checked');
				$(".immediately").prop('checked',true);
			}
		},

		listReleases: function() {
			var self = this,
				params = qd.utils.serialize(self.$el.find('.qd_query_params'));
			$.extend(params, { pager: self.page_info });
			qd.rpc("upgrade.ComponentUpgradeApi.query_versions", params).success(function(result) {
				qd.render_template('data_list_table', result, '.data_list_div');
			});
		},

		/**
		 * 通过oid删除版本记录
		 * @param tr
		 */
		remove_release2: function(tr) {
			var self = this;
			if(!window.confirm("你确定要删除此版本?")) { return }
			var oid = $(tr).data('oid');
			var params = { oid: oid };
			qd.rpc("upgrade.ReleaseApi.remove_release2", params).success(function(result) {
				if(result.err == 0) { $(tr).remove(); }
			});
		},
		_validate1: function(params) {
			var self = this,
				_rs = true;

			var definition = self.$el.find('#add_version_release_form input[name=json_file]').val();
			var package = self.$el.find('#add_version_release_form input[name=bin_file]').val();
			//var shell = self.$el.find('#add_version_release_form input[name=myfiles].shell').val();

			if(definition == '') {
				_rs = false;
				qd.notify.error('请选择上传的定义文件');
			} else if(package == '') {
				_rs = false;
				qd.notify.error('请选择上传的升级包文件');
			}

			return _rs;
		},
		submit: function() {
			var self = this;
			var params = qd.utils.serialize(self.$el.find('#add_version_release_form'));
			if ($(".immediately_div").attr('style')=='display: none;') {
				params.release_at = $(".startTime").val();
			} else{
				params.release_at = "";
			}
			if(!self._validate1(params)) { return; }
			if(!window.confirm('提交前，请仔细核对信息。\n\n你确认要发布此版本？')) { return; }

			if(self.token) {
				self.token = false;
				var oProgress = $('.progress').show();
				$('#add_version_release_form').ajaxSubmit({
					url: '/remote/upgrade.ComponentUpgradeApi.release_version/',
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
						$('#add_version_release_form').get(0).reset();
						$('#upgrade_window').modal('hide');
					},
					complete: function(xhr, ts) {
						oProgress.hide();
						$('#percent').css('width', '0');
						self.token = true;
					}
				});
			}
		}

	});

	/**
	 * 网关升级
	 * @type {any}
	 */
	mm.AgwUpgradeView = Backbone.View.extend({
		className: 'view_box',
		token: true,
		_ejs: '/static/upgrade/tpls/agw_upgrade_list.ejs',
		_tpl: '/static/upgrade/tpls/agw_release.tpl',
		initialize: function() {
			var self = this;
			this.cache_collection = [];
			qd.load_view_tpls(self._tpl);
			var ejs_html = new EJS({ url: this._ejs }).render({});
			$(this.el).html(ejs_html);
			$(app_router.content).html(this.el);
			this.page_info = { page_no: 1, page_size: 10 };
			this.listReleases();
		},

		events: {
			'click .qd_query_params .query_btn': function(evt) {
				this.page_info.page_no = 1;
				this.listReleases();
			},
			'click .data_list_div ul.pagination>li': function(evt) {
				var page_no = $(evt.currentTarget).data('page_no');
				if(!page_no) { return; }
				this.page_info.page_no = page_no;
				this.listReleases();
			},
			'click .submit-version-release-btn': function(evt) {
				this.submit();
			},
			'change #file_test': function(evt) {
				console.log(456);
			}
		},

		listReleases: function() {
			var self = this,
				params = qd.utils.serialize(self.$el.find('.qd_query_params'));
			//$.extend(params, {pager: self.page_info});

			qd.rpc("upgrade.AgwUpgradeApi.list_versions", { pager: self.page_info })
				.success(function(result) {
					qd.render_template('data_list_table', result, '.data_list_div');
				});
		},
		_validate1: function(params) {
			var type_name = this.$el.find('#agw_release_form input[name=type_name]').val(),
				version = this.$el.find('#agw_release_form input[name=version]').val(),
				package = this.$el.find('#agw_release_form input[name=bin_file]').val();

			if(type_name == '') {
				qd.notify.error('请输入上传文件的类型');
				return false;
			}

			var reg = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/;

			if(!reg.test(version)) {
				qd.notify.error('请输入有效版本号');
				return false;
			}

			if(package == '') {
				qd.notify.error('请选择上传的升级包文件');
				return false;
			}

			return true;
		},
		submit: function() {
			var self = this,
				params = qd.utils.serialize(self.$el.find('#agw_release_form'));
			if(!self._validate1(params)) { return; }
			if(!window.confirm('提交前，请仔细核对信息。\n\n你确认要发布此版本？')) { return; }
			if(self.token) {
				self.token = false;
				var oProgress = $('.progress').show();
				$('#agw_release_form').ajaxSubmit({
					url: '/remote/upgrade.AgwUpgradeApi.release_bin_file/',
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
						$('#agw_release_form').get(0).reset();
						$('#upgrade_window').modal('hide');
						self.listReleases();
					},
					complete: function(xhr, ts) {
						oProgress.hide();
						$('#percent').css('width', '0');
						self.token = true;
					}
				});
			}
		}

	});

})(jQuery);