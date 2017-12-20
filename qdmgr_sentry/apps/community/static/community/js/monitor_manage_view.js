var brake_monitor_manage_view = Backbone.View.extend({
    template: versionify(CONST.static_url+'community/ejs/monitor_manage_block.html'),
    page_no: 1,
    page_size: 50,
    type: "add",

    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
        this.loadData();
    },
    loadData: function () {
        this.getList();
    },
    getList:function(){
        var _this = this;
        $.ajax({
            url: '/brake_api/Brake_Alert_Api/get_alerter/1/',
            type: 'POST',
            data:{
                web_user_id:$('input[name="web-user-id"]').val()
            },
            dataType: 'json',
            success: function(result) {
                if(result.data.flag === "Y"){
                    var ejs_html = new EJS({url: CONST.static_url+'community/ejs/monitor_manage_list_block.html?'+ Math.random()})
                    .render({list: result.data.brake_alert_list});
                    $(_this.el).find(".list-block").html(ejs_html); 
                }
            }
        });    	
    },
    
    addMonitor: function (web_user_id, val) {
        $.ajax({
            url: '/brake_api/Brake_Alert_Api/add_alerter/1/',
            type: 'POST',
            data: {
                web_user_id: web_user_id,
                alert_email: val
            },
            context: this,
            success: function() {
                $('#edit_modal').modal('hide');
                this.getList();
            }
        });
    },
    editMonitor: function (id, val) {
        $.ajax({
            url: '/brake_api/Brake_Alert_Api/set_alerter/1/',
            type: 'POST',
            data: {
                alert_id: id,
                alert_email: val
            },
            context: this,
            dataType: "json",
            success: function(result) {
                if(result.data.flag === "Y"){
                    $('#edit_modal').modal('hide');
                    this.getList();
                } else if(result.data.flag === "N"){
                    UI.showErrTip(result.msg);
                }
            }
        });  
    },
    events: {
		// 添加监控人
		'click .add-monitor-btn':function(){
            $('#edit_title').html('添加监控人');
            $('input[name="edit_item_id"]').val("");
            $('#alert_email').val("");
            $('#edit_modal').modal('show');
            this.type = "add";
		},
        // 编辑监控人
        'click .edit-item-btn': function(event) {
            var item = $(event.srcElement || event.target).parents('tr');
            $('#alert_email').val(item.data("email"));
            $('#edit_title').html('编辑监控人');
            $('#edit_modal').modal('show');
            $('input[name="edit_item_id"]').val(item.data("item-id"));
            this.type = "edit";
        },
		// 删除监控人
		'click .remove-item-btn':function(event){
            if (!confirm('确定要删除吗？')) return true;
            var item = $(event.srcElement || event.target).parents('tr');
            $.ajax({
                url: '/brake_api/Brake_Alert_Api/delete_alerter/1/',
                type: 'POST',
                context:this,
                data: {
                    alert_id: item.data('item-id')
                },   
                dataType: 'json',
                success: function() {
                    item.remove();
                    UI.showSucTip('删除成功');
                }
            });
		},    	
        // 确定提交
        'click .edit-submit-btn': function() {
            var id = $('input[name="edit_item_id"]').val();
            var web_user_id = $('input[name="web-user-id"]').val();
            var val = $('#alert_email').val();
            var reg_email = /^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/;
            if (!reg_email.test(val)) {
                UI.showErrTip("请输入正确的邮件地址");
                return true;
            } 
            if( this.type === "add"){
                this.addMonitor(web_user_id, val);
            }else{
                this.editMonitor(id, val);
            }
            
        }

    }
});

