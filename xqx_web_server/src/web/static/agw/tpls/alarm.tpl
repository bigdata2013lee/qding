<script type="text/template" name="view_template">
<div>
    <h4>报警网关/报警记录</h4>
    <div class="query_box" data-template="query_box">
        <form class="form-inline phase_build_select" role="form">
            <div class="form-group">
                <label class="control-label">组团/期</label>
                 <input type="number" name="phase_no" class="form-control" min="1" placeholder="请输入组团/期"/>
            </div>

            <div class="form-group">
                <label class="control-label">楼栋</label>
                <input type="number" name="building_no" class="form-control" min="1" placeholder="请输入楼栋"/>
            </div>

            <div class="form-group">
                <label class="control-label">房间号</label>
                <input name="aptm_short_code" class="form-control" placeholder="请输入房间号"/>
            </div>

            <button type="button" class="btn btn-primary query_btn"> 查询 </button>
        </form>
    </div>
    <div class="data_list_box" data-template="devices"></div>
</div>
</script>

<script type="text/template" name="devices_template">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>房间</th>
                <th>类型</th>
                <th>端口</th>
                <th>时间</th>
                <th>状态</th>
            </tr>
        </thead>

        <tbody>
            <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
            <tr data-oid="<%=item.id%>">
                <td><%=item.aptm_pre_names[0]%><%=item.aptm_name%></td>
                <td><%=qd.choices.alarm_types[item.alarm_type]%>报警</td>
                <td>#<%=item.alarm_id%></td>
                <td><%=new Date(item.created_at).format('yyyy/MM/dd hh:mm')%></td>
               	<%= item.deal_status === 'undealed' ? "<td>未处理</td>" : "<td>已处理</td>" %>
            </tr>
            <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>
