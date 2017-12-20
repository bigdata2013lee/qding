var scan_data_view = Backbone.View.extend({
    _tpl:CONST.static_url+'manage/ejs/scan_data_content.tpl',
    page_no:1,
    page_size:50,
    scan_result: {
        "req_count": 0,
    },
    initialize:function(){
        qd.load_view_tpls(this._tpl);
        $(this.el).render_template({},"view");
        var view = this;
        view.get_total_pass_data();
        view.get_total_project_data();
        view.get_total_brake_machine_data();
    },

    rand_html: function() {
        this.$el.find(".scan_data").render_template(this.scan_result);
    },

    get_total_pass_data:function(){
        var view = this;
        $.ajax({
            url:'/brake_api/Brake_Pass_Api/get_all_pass_count/1/',
            type:'POST',
            data:{},
            dataType:'json',
            success: function (result) {
                view.scan_result.pass_count = result.data.pass_count;
                view.scan_result.req_count += 1;
                if(view.scan_result.req_count >= 3){
                    view.rand_html();
                }
            }
        });
    },

    get_total_project_data:function(){
        var view = this;
        $.ajax({
            url:'/basedata_api/Basedata_Project_Api/get_all_project_count/',
            type:'POST',
            data:{},
            dataType:'json',
            success:function(result){
                view.scan_result.project_count = result.data.project_count;
                view.scan_result.req_count += 1;
                if(view.scan_result.req_count >= 3){
                    view.rand_html();
                }
            }
        });
    },

    get_total_brake_machine_data:function(){
        var view = this;
        $.ajax({
            url:'/brake_api/Brake_Machine_Api/get_all_brake_machine_count/1/',
            type:'POST',
            data:{},
            dataType:'json',
            success:function(result){
                view.scan_result.brake_machine_count = result.data.brake_machine_count;
                view.scan_result.req_count += 1;
                if(view.scan_result.req_count >= 3){
                    view.rand_html();
                }
            }
        });
    },

    events:{

    }
});