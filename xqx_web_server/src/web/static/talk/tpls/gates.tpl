<script type="text/template" name="view_template">
    <div>
        <h4>对讲/门口机</h4>
        <div class="query_box" data-template="query_box">
            <form class="form-inline phase_build_select" role="form">
                <div class="form-group" style="margin-right: 20px;">
                    <label class="control-label">类型</label>
                    <select name="dev_type" class="form-control">
                        <option value="">请选择门口机类型</option>
                        <option value="Gate.UnitGate">单元门口机</option>
                        <option value="Gate.FenceGate">围墙门口机</option>
                    </select>
                </div>
                <div class="form-group" style="margin-right: 20px;">
                    <label class="control-label">状态</label>
                    <select name="heartbeat_status" class="form-control">
                        <option value="">请选择在线状态</option>
                        <option value="up">在线</option>
                        <option value="down">离线</option>
                    </select>
                </div>
                <button type="button" class="btn btn-primary query_btn"> 查询 </button>
            </form>
        </div>
        <div class="data_list_box" data-template="gates"></div>
    </div>
</script>

<script type="text/template" name="gates_template">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>设备</th>
                <th>状态</th>
                <th>门磁</th>
                <th>版本</th>
            </tr>
        </thead>
        <tbody>
            <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
            <tr data-oid="<%=item.id%>">
                <td><%= qd.choices.gate_types[item._cls] %> <%=item.name%></td>
                <td>
                    <%= item.heartbeat.status === 'up' ? "<span style='color:#449d44;'>在线</span>" : "<span style='color:#d9534f;'>离线</span>" %>
                    <span class="time"><%=new Date(item.heartbeat.at).format('yyyy/MM/dd hh:mm')%></span>
                </td>
                <td> <%= item.heartbeat.is_locked ? "<span style='color:#d9534f;font-weight: bold;'>开</span>" : "<span style='color:#449d44;font-weight: bold;'>关</span>"%></td>
                <td>Rom: <%=item.versions.rom_version%>  App: <%=item.versions.app_version%></td>
            </tr>
            <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>
