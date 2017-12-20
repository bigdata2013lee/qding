<script type="text/template" name="view_template">

<div>

    <h4>报警网关/网关设备</h4>
    <div class="query_box" data-template="query_box">
        <form class="form-inline phase_build_select" role="form">
            <div class="form-group">
                <label class="control-label">组团/期</label>
                <input type="number" name="phase_no" class="form-control" min="1" placeholder="请输入组团/期"/>
            </div>

            <div class="form-group">
                <label class="control-label">楼栋</label>
                 <input type="number" name="building_no" class="form-control" min="1" placeholder="请输入组团/期"/>
            </div>

            <div class="form-group">
                <label class="control-label">房间号</label>
                <input name="aptm_short_code" class="form-control" placeholder="请输入房间号" />
            </div>

            <button type="button" class="btn btn-primary query_btn"> 查询 </button>
        </form>
    </div>

    <div class="data_list_box" data-template="devices"></div>

    <div class="modal fade" id="alarm_areas_window" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title">报警布/撤防</h4>
                </div>
                <div class="modal-body" data-template="alarm_areas_window_body">

                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal">取消</button>
                    <button type="button" class="btn btn-primary submit_btn"> 保存设置 </button>
                </div>

            </div>
        </div>
    </div>

</div>
</script>

<script type="text/template" name="query_box_template">

    <form class="form-inline" role="form">
        <div class="form-group">
            <label class="control-label">组团/期
                <small style="color:red;">*</small>
            </label>
            <select name="phase_id" class="form-control">
                <option value="">--Please Select Phase--</option>
                <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
                <option value="<%=item.id%>"><%=item.name%></option>
                <%}%>
            </select>
        </div>

        <button type="button" class="btn btn-default query_btn"> 查询 </button>
    </form>

</script>


<script type="text/template" name="devices_template">
    <table class="table table-striped table-hover">
        <thead>
            <tr>
                <th>房间号</th>
                <th>MAC地址</th>
                <th>版本号</th>
                <th>当前状态/最后在线时间</th>
                <th>操作</th>

            </tr>
        </thead>

        <tbody>
            <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
            <tr data-oid="<%=item.id%>">
                <td><%=item.aptm_pre_names[1] + item.aptm_pre_names[2]%><%=item.aptm_name%></td>
                <td><%=item.mac%></td>
                <td>hw:<%=item.hw_version%>, sw:<%=item.sw_version%>, wifi:<%=item.wifi_version%>, res:<%=item.res_version%></td>
                <td>
                    <%= item.heartbeat.status === 'up' ? "<span style='color:#449d44;'>在线</span>" : "<span style='color:#d9534f;'>离线</span>" %>
                   <span class="time"><%=new Date(item.heartbeat.at).format('yyyy/MM/dd hh:mm')%></span>
                </td>
                <td>
                    <a href="javascript:" name="alarm_areas_btn" data-target="#alarm_areas_window" data-toggle="modal">
                    <i class="glyphicon glyphicon-bell"></i> 布/撤防
                    </a>
                </td>
            </tr>
            <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>

<script type="text/template" name="alarm_areas_window_body_template">
<style>
    .wrap{
        width: 45px;
        height: 20px;
        border-radius: 18px;
        position: relative;
        cursor: pointer;
    }

    .wrap .status{
        display: inline-block;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        margin: 2px 0 0 5px;
        background: #FFFFFF;
    }

    .bg1{
        background: #4cd964;
    }

    .bg2{
        background: #E6E6E6;
    }

    .toRight{
        transform: translate3D(20px, 0, 0);
        transition: .5s ease;
    }

    .toLeft{
        transform: translate3D(0, 0, 0);
        transition:  .5s ease;
    }
</style>
<div class="win_context_title">
    设备: <%=data.agw.aptm_pre_names[0]%><%=data.agw.aptm_name%> <%=data.agw.mac%>
    <input type="hidden" name="agw_id" value="<%=data.agw.id%>"/>
</div>
<table class="table table-hover">
        <thead>
            <tr>
                <th>#</th>
                <th>类型</th>
                <th>位置</th>
                <th>当前状态</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
        <% for(var i=0; i<data.agw.alarm_areas.length; i++){ var item = data.agw.alarm_areas[i]; %>
        <tr data-alarm_id="4" class="alarm_tr">
            <td>#<%=item.alarm_id%></td>
            <td><%= qd.choices.alarm_types[item.alarm_type] %></td>
            <td><%=item.loc_name%></td>
            <td><%= item.enable ? "<span style='color:#449d44;'>布防</span>" : "<span style='color:#d9534f;'>撤防</span>" %></td>
            <td>
                <div class="wrap <%=item.enable? 'bg1' : 'bg2' %>"  data-name="alarm_<%=item.alarm_id%>" data-value="<%=item.enable? 'true' : 'false' %>" >
                    <div class="status <%=item.enable? 'toRight' : 'toLeft' %>"></div>
                </div>
            </td>
        </tr>
        <%}%>
        </tbody>
    </table>
</script>
