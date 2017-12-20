var brake_data_statistics_view = Backbone.View.extend({
    template: versionify(CONST.static_url+'community/ejs/data_statistics_block.html'),
    page_no: 1,
    page_size: 50,
    isToday: true,
    start_day: null,
    end_day: null,
    d_year:null,
    d_month:null,
    now_year:null,
    now_month:null,

    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
        this.loadData();
    },
    loadData: function () {
        var d = new Date();
        this.now_year = d.getFullYear();
        this.now_month = d.getMonth();
        this.setDateInfo();
        this.getList();
    },
    getList:function(startDay, endDay){
        if(typeof pageIndex == "undefined"){
            this.page_no = 1;
            this.page_inited = false;
        }
        var _this = this;
        $.ajax({
            url: '/brake_api/Brake_Pass_Api/get_community_day_pass_count/1/',
            type: 'POST',
            data: {
                start_day: _this.start_day,
                end_day: _this.end_day,
                province: $("#sProvince").html(),
                city: $("#sCity").html(),
                community: $("#sCommunity").html()
            },   
            dataType: 'json',
            success: function(result) {
                if(result.data.flag === "Y"){
                    var ejs_html = new EJS({url: CONST.static_url+'community/ejs/data_statistics_list_block.html?'+ Math.random()})
                    .render({});
                    $(_this.el).find('.list-block').html(ejs_html); 
                    _this.loadChart(result.data.day_pass_count_list);
                }
            },
            error: function () {
                alert("数据加载失败，请联系系统管理员");
            }
        });    	
    },
    // 创建图表
    loadChart: function(data){
        var categories=[];
        var series = [];
        var series_two = [];
        var series_all = [];
        var len = data.length;
        for(var i=0; i< len; i++){
            categories.push(data[i]["day"]);
            series.push(data[i]["cummunity_gate_pass_num"]);
            series_two.push(data[i]["unit_gate_pass_num"]);
            series_all.push(data[i]["cummunity_gate_pass_num"] + data[i]["unit_gate_pass_num"]);
        }
        // 修改默认值
        this.dataDefault.xAxis.categories = categories;
        this.dataDefault.series = [
            {"name":"大门通行次数","data":series},
            {"name":"单元门通行次数","data":series_two},
            {"name":"总通行次数","data":series_all}
        ];
        $("#graphic").highcharts(this.dataDefault);
    },
    // 计算该年该月有多少天
    dayNumOfMonth: function (year,month){
        var d = new Date(year,month,0);
        return d.getDate();
    },
    // 计算该年该月有多少天
    setDateInfo: function (Year, Month){
        var year, month, date;
        if(Month != undefined){
            year = Year;
            month = Month;
            date = this.dayNumOfMonth(Year, Month+1);
            $("#nextMonth").prop("disabled", false);
        } else {
            var d = new Date;
            year = d.getFullYear();
            month = d.getMonth();
            date = d.getDate();
            //this.isToday = true;
            
            $("#nextMonth").prop("disabled", true);

        }
        this.setDateStep(date);
        //console.log(year+"年"+(month+1)+"月"+date+"日");
        this.start_day = parseInt(new Date(year,month,1).getTime()/1000);
        this.end_day = parseInt(new Date(year,month,date+1).getTime()/1000);
        this.d_year = year;
        this.d_month = month;
    },
    computeYearMonth: function (month, num){
        this.d_month = month + num;
        if(this.d_month < 0){
            this.d_month = 11;
            this.d_year = this.d_year + num;
        } else if(this.d_month > 11){
            this.d_month = 0;
            this.d_year = this.d_year + num;
        }
    },
    setDateStep: function (date) {
        if(date < 8){
            this.dataDefault.xAxis.labels.step = 1;
        } else if(date < 14){
            this.dataDefault.xAxis.labels.step = 2;
        } else if(date < 20){
            this.dataDefault.xAxis.labels.step = 3;
        } else if(date < 26){
            this.dataDefault.xAxis.labels.step = 4;
        } else {
            this.dataDefault.xAxis.labels.step = 5;
        }
    },
    
    
    events: {
		// 添加邮件接收人
		'click .edit-add-email-btn':function(){
			$("#alert_email_list").append(this.createEmail(email=""));
			this.addIndex++;
		},
		// 删除邮件接收人
		'click .edit-del-email-btn':function(event){
			$(event.srcElement || event.target).parent().remove();
		},    	
    	
        'click .edit-item-btn': function(event) {
            var item = $(event.srcElement || event.target).parents('tr');
            $('#heart_time').val(item.data("heart-time"));
            $('#edit_modal').modal('show');
            $('input[name="edit_item_id"]').val(item.data("device-id"));
        },

        'click .bootstrap-switch': function(event) {
            var item = $(event.srcElement || event.target).parents('.bootstrap-switch');
            var tr = item.parents('tr');
            var edit = tr.find(".operate-edit");
            var cls = item.attr("class").indexOf("switch-on");
            if(cls > 0){
                edit.addClass("edit-item-btn");
                this.setMonitoring(tr.data("device-id"), 1);
            } else {
                edit.removeClass("edit-item-btn");
                this.setMonitoring(tr.data("device-id"), 0);
            }
        },

        'click .edit-submit-btn': function() {
            var id = $('input[name="edit_item_id"]').val();
            var val = $('#heart_time').val();
            var reg = /^\d*$/;
            if (!reg.test(val)) {
                UI.showErrTip("请输入正确的报警间隔时间");
                return true;
            } 
            $.ajax({
                url: '/brake_api/Brake_Machine_Api/set_brake_heart_time/1/',
                type: 'POST',
                data: {
                    brake_id: id,
                    heart_time: val
                },
                context: this,
                dataType: 'json',
                success: function() {
                    $('#edit_modal').modal('hide');
                    this.getList();
                }
            });
        },
        'click #prevMonth': function() {
            //this.isToday = false;
            $("#nextMonth").prop("disabled", true);
            this.computeYearMonth(this.d_month, -1);
            this.setDateInfo(this.d_year, this.d_month);
            this.getList();
        },
        'click #nextMonth': function() {
            this.computeYearMonth(this.d_month, 1);
            if(this.now_month === this.d_month && this.now_year === this.d_year){
                $("#nextMonth").prop("disabled", true); 
                //this.isToday = true;
                this.setDateInfo();
            } else {
                this.setDateInfo(this.d_year, this.d_month);
            }
            this.getList();
        }

    },
    // =======================图表数据结构 start======================================
    dataDefault: {
    	colors: ['#058DC7', '#434348', '#90ED7D'],
        title: {
            text: ' '
        },
        subtitle: {
            text: '单位(次)',
            align: "left"
        },
        lang: {
            noData: "暂无数据"
        },
        xAxis: {
            //tickWidth: 0,
            labels: {
                step: 5,
                staggerLines: 1,
                style: {color: '#333333'},
                x: -8
            },
            offset: 25
            // categories: ['0时', '1时', '2时', '3时', '4时', '5时', '6时', '7时', '8时', '9时', '10时', '11时', '12时', '13时', '14时', '15时', '16时', '17时', '18时', '19时', '20时', '21时', '22时', '23时','24时']
        },
        yAxis: {
            //floor: 0,
            title: {
                text: ''
            },
            labels: {
                step: 1,
                style: {color: '#333333'}
            },
            min: 0
        },
        tooltip: {
            valueSuffix: ''
        },
        legend: {
            layout: 'horizontal',
            align: 'right',
            verticalAlign: 'top',
            borderWidth: 0,
            floating: true
        },
        credits:{ // 版权
            enabled: false
        },
        series: []/*[{
            name: '项目1',
            color: 'red',
            data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
        }, {
            name: '项目2',
            data: [-0.2, 0.8, 5.7, 11.3, 17.0, 22.0, 24.8, 24.1, 20.1, 14.1, 8.6, 2.5]
        }]*/
    }
});

