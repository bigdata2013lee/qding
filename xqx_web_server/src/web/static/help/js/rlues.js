/**
 * 计费规则模块
 */

;(function(w,$){

    function getParams(url) {
        var params = {};
        (url ||  window.location.href).replace(/[?&]+([^=&]+)=([^&]*)/gi, function(str, key, value) {
            params[key] = value;
        });
        return params;
    }

    //获取计费规则
    var oLoaing = $("#loading").show();
    $.ajax({
        type: "POST",
        url: "http://www.wuzhelu.com:7084/park/overview",
        data: {parkId: getParams().parkId},
        dataType: "json",
        success: function(data){
            if(data.code === 0){
                data.data.list.forEach(function(rulesArr, index){
                    createRulesTables(rulesArr, index);
                });
            }else{
                $("#layer").show();
            }
        },
        error: function(){
            $("#layer").show();
        },
        complete: function(){
            oLoaing.hide();
        }
    });

    function formatRuleTime( item, attr ){
        var html = 0, parkTime = Number(item[attr]);

        if(parkTime > 60 && parkTime % 60 != 0){

            html = "首" + (parkTime - parkTime % 60) / 60 + "小时" + parkTime % 60 + "分钟";

        } else if(parkTime % 60 == 0){

            html = (parkTime / 60  == 1) ? "首小时" : "首" + (parkTime / 60) + "小时";

        }else{

            html = "首" + parkTime + "分钟";

        }

        return html;
    }

    //解析规则
    function createRulesTds(listTrs){
        var tr = "",  perRuleRowspan = 1, inParkRuleRowspan = listTrs.inParkRule.length + perRuleRowspan;
        listTrs.inParkRule.forEach(function (item, index)  {
            var m1 = (Number(item.inParkTimeCost) / 100 == 0) ? "免费" : (Number(item.inParkTimeCost) / 100 + "元");
            if(index == 0){
                tr += "<tr>";
                tr +=     "<td rowspan='"+ inParkRuleRowspan +"'>";
                tr +=        listTrs.carType;
                tr +=     "</td>";
                tr +=     "<td>";
                tr +=        formatRuleTime( item, 'inParkTime' );
                tr +=     "</td>";
                tr +=     "<td>"+ m1 + "</td>";
                tr += "</tr>";
            }else{
                tr += "<tr>";
                tr +=     "<td>";
                tr +=        formatRuleTime( item, 'inParkTime' );
                tr +=     "</td>";
                tr +=     "<td>"+ m1 + "</td>";
                tr += "</tr>";
            }
        });

        var tr1 = "";
        listTrs.perRule.forEach(function (item, index)  {
            if(Number(item['perTime']) == 60){
                tr1 = "";
                tr1 += "<tr>";
                tr1 +=     "<td>每小时</td>";
                tr1 +=     "<td>"+  Number(item.perCost) / 100 + "元</td>";
                tr1 += "</tr>";
            }
        });

        return tr +  tr1;
    }

    function createRulesTables(lists, index){
        var className = index % 2 == 0 ? "tabs1 tabs2" : "tabs1", rules = "<br/><div style='margin: 0 10px;'><table cellpadding='0' cellspacing='0' class='"+ className +"'>";
        rules += "<tr><td colspan='3'>"+ lists.timeBucket  +"</td></tr>";
        lists.listAll.forEach(function (listTrs)  {
            rules += createRulesTds( listTrs );
        });
        rules += "</table></div>";
        $("body").prepend(rules);
    }

})(window, Zepto);















