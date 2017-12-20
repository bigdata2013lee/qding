var modify_password_view = Backbone.View.extend({
    template: versionify(CONST.static_url+'community/ejs/modify_password_block.html'),
    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
    },
    // 错误提示
    showTips: function(type, msg) {
        $('.notifications').notify({
            type: type,
            fadeOut: {
                enabled: true,
                delay: 3000
            },
            message: {
                text: msg
            }
        }).show();
    },
    
    events: {
    	'click .save-pw-btn':function(event){
    		var old_pw_val = $('#oldPW').val();
            var new_pw_val = $('#newPW').val();
            var new_pw_sure_val = $('#newPWSure').val();
    		if( !new_pw_val || !new_pw_sure_val || !old_pw_val){
                this.showTips('danger', '请填写完整信息');
    			return false;
    		} else if(new_pw_val !== new_pw_sure_val){
                this.showTips('danger', '两次密码输入不一致');
                return false;   
            }
    		$.ajax({
    			url: '/user_api/Web_User_Api/modify_user/1/',
    			type: 'POST',
    			data: {
    				user_id: $("#userId").html(),
    				old_password:$.md5(old_pw_val),
                    password: $.md5(new_pw_val),
    			},
    			dataType: 'json',
                context: this,
    			success:function(result){
    				if(result.data.flag === "Y"){
                        this.showTips('info', '密码修改成功');
                        setTimeout(function(){
                            window.location.href="/content";
                        }, 2000)
    				} else {
    					this.showTips('danger', result.msg);
                        return false;   
        				
    				}
    			}
    		});
    	}
    }
});

