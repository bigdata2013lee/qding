<script type="text/template" name="data_list_table_template">
    <table class="table table-hover table-striped">
        <thead>
        <tr>
            <th></th>
            <th style="width: 180px">文件类型</th>
            <th>版本</th>
            <th>发布时间</th>
        </tr>
        </thead>
        <tbody>
        <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i];%>
        <tr data-oid="<%=item.id%>">
            <td><%if(item.active){%><i class="glyphicon glyphicon-ok" style="color: green"></i><%}%></td>
            <td><%= item.fi_type_name %></td>
            <td><%= item.version %></td>
            <td>
                <%= new Date(item.created_at).format("yyyy/MM/dd hh:mm") %>
                <%if(item.delay > 0){%>
                <br/><span style="color: #aaa;"> (离发布时间<%= item.delay%>小时后生效)</span>
                <%}%>
            </td>
        </tr>
        <%}%>
        </tbody>
    </table>

    <%=qd.mk_pagination(data.pagination)%>
</script>