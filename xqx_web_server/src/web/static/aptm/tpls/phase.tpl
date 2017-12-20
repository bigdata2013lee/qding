<script type="text/template" name="view_template">
<div>

    <style>
        div.data_list_box>ul{list-style: none; padding:0; margin: 0}
        div.data_list_box>ul>li{list-style: none; padding:0; margin: 0}
        div.data_list_box>ul>li>div.header{
            background-color: #efefef;
            padding:0.5em;
        }
    </style>
    <h4>管理/期(组团)-楼栋</h4>

    <div class="alert alert-info" role="alert">
        双击名称进行编辑，请勿随意更改名称，建议以[一期][二期]字样命名期，以[1栋][2栋][3栋]字样命名楼栋。
    </div>


    <div class="data_list_box" data-template="phase_list"></div>

</div>

</script>




<script type="text/template" name="phase_list_template">

<ul>
    <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
    <li data-phase_id="<%=item.id%>">
       <div class="header"><h4><span><%=item.name%></span></h4></div>
       <div class="data_body" data-template="building_list"></div>
    </li>
    <%}%>
</ul>
</script>


<script type="text/template" name="building_list_template">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>名称</th>
                <th>序号</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
            <tr data-building_id="<%=item.id%>">
                <td><span><%=item.name%></span></td>
                <td><%=item.building_no%></td>
                <td></td>
            </tr>
            <%}%>
        </tbody>
    </table>
</script>