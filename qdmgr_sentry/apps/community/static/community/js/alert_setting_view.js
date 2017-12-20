var alert_setting_view = Backbone.View.extend({
	template: versionify(CONST.static_url+'community/ejs/alert_settinig_block.html'),
	initialize:function(){
		$(this.el).html(new EJS({url:this.template}).render({}));
		var view=this;
		this.get_alert();
	},
	
	get_alert:function(){
        $.ajax({
            url: '/brake_api/Brake_Alert_Api/get_alerter/1/',
            type: 'POST',
            data: {
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                community: $("#sCommunity").html()                
            },   
            dataType: 'json',
            success: function(result) {
            	$('#alert_email').val(result.data.alert_email);
            	$('#alert_time').val(result.data.alert_time);
            }
        });	
	},
	
    events: {
    	'click .alert-setting-btn':function(){
    		// 判断是否绑定了小区
    		var communityName = $("#communityName").html();
			if (!communityName) {
				UI.showTips('danger', '请先绑定小区');
				return false;
			}

			var time_val = $("#alert_time").val();
			var email_val = $("#alert_email").val();
			var time_reg = /^[1-9][0-9]*$/;
			var email_reg = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
			if (!time_val || !email_val) {
				UI.showErrTip('请填写完整信息');
				return false;
			}
			if (!time_reg.test(time_val)) {
				UI.showErrTip('请填写正确的告警间隔时间');
				return false;
			}
			if (!email_reg.test(email_val)) {
				UI.showErrTip('请填写正确的邮箱地址');
				return false;
			}
			$.ajax({
				url: '/brake_api/Brake_Alert_Api/set_alerter/1/',
				type: 'POST',
				data: {
					province: $("#sProvince").html(),
					city: $("#sCity").html(),
					community: $("#sCommunity").html(),
					alert_time: time_val,
					alert_email: email_val
				},
				dataType: 'json',
				success: function(result) {
					if (result.data.flag === "Y") {
						UI.showSucTip('提交成功');
					} else {
						UI.showErrTip('提交失败，请联系系统管理员');
					}
				}
			});
    	}
    }
});