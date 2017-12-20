(function($) {

	var mm = qd.ns("views.project");

	mm.password = Backbone.View.extend({
		className: 'view_box',
		_tpl: '/static/qd/password/tpls/password.tpl',
		token: true,
		_query_pager: {},
		initialize: function() {
			console.log(456);
			qd.load_view_tpls(this._tpl);
			$(this.el).render_template({}, 'view');
			$(app_router.content).html(this.el);
		},
		events: {
			"click div.submit_box .submit_btn": function(evt) {
				this.submitbut();
			}
		},
		_v: function(params) {
			var rules = {
				"old_password": "required",
				"new_password": { "method": "regex", exp: /^[#@_\-A-Za-z0-9]{4,30}$/ },
				"confirm_passwd": { "method": "confirmPassword", eqto: "new_password" }
			};
			var messages = {
				"old_password": "请输入旧密码",
				"new_password": "密码格式错误"
			};
			var v = new qd.utils.Validator(rules, messages);
			return v.validate(params);

		},
		submitbut: function() {
			var params = qd.utils.serialize('div.submit_box');
			if(!this._v(params)) return;
			delete params.phase_id;
			delete params.confirm_passwd;
			qd.rpc("wuye.WuyeUserApi.wy_change_pwd", params);
		}
	});

})(jQuery);