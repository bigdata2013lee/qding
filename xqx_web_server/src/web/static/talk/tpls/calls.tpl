<script type="text/template" name="view_template">
    <div>

        <h4>对讲/通话记录</h4>
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
                    <label class="control-label">房间码</label>
                    <input name="aptm_short_code" class="form-control" placeholder="请输入房间码" />
                </div>

                <button type="button" class="btn btn-primary query_btn"> 查询 </button>
            </form>

        </div>

        <div class="data_list_box" data-template="calls_list"></div>

    </div>
</script>

<script type="text/template" name="calls_list_template">
    <table class="table table-striped table-hover">
        <thead>
        <tr>
            <th>接听人</th>
            <th>呼叫</th>
            <th>状态</th>
        </tr>
        </thead>
        <tbody>
        <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
        <tr data-oid="<%=item.id%>">
            <td><%=item.to_desc%></td>
            <td><%=item.from_desc%></td>
            <td><span class="time"><%=new Date(item.created_at).format('yyyy/MM/dd hh:mm')%></span>&nbsp;&nbsp;<%= item.is_received ? "<span style='color:#449d44;'>已接听</span>" : "<span style='color:#d9534f;'>未接听</span>"%><%=item.duration ? "(" + item.duration +"秒)" : "" %></td>
        </tr>
        <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>
