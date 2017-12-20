<script type="text/template" name="view_template">
    <div class="page-header">
        <b class="" style="font-size:18px;">卡管理 - 用户卡</b>
    </div>

    <div class="operate-box card-search-box" data-template="card_search_box"></div>

    <div class="list-block" data-template="card_list"></div>
    <div class="pagination-wrap">
        <div class="pagination-con" id="pagination"></div>
    </div>

    <div id="edit-card-modal" class="modal fade" data-backdrop="static" data-keyboard="false">
        <div class="modal-dialog" style="width:630px; margin-top:100px;">
            <div class="modal-content">
                <div class="modal-header">
                    <b class="text-muted">修改卡</b>
                    <button class="close" data-dismiss="modal" title="关闭">
                        <i class="fa fa-times"></i>
                    </button>
                </div>
                <div class="modal-body" data-template="card_info">
                </div>
                <div class="modal-footer">
                    <a class="btn btn-info submit-card-btn">
                        <span>确定</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</script>

<script type="text/template" name="card_info_template">
    <input name="card-id" type="hidden" value="<%= id %>"/>
    <div class="form-horizontal" style="margin-left:-20px;">
        <table width="580">
            <tr class="modify-card-status-tr">
                <td width="100" align="right" class="form-cell" valign="top">
                    <span class="text-muted">修改状态</span>
                </td>
                <td class="cell-split">
                    <select name="card-status" class="form-control modify-card-status-select w200">
                        <option value="" <%= status == "" ? "selected" : "" %>>--请选择--</option>
                        <option value="2" <%= status == "1" ? "selected" : "" %>>注销中</option>
                        <option value="4" <%= status == "3" ? "selected" : "" %>>激活中</option>
                    </select>
                </td>
            </tr>
            <tr class="modify-card-phone-tr">
                <td width="100" align="right" class="form-cell" valign="top">
                    <span class="text-muted">手机号</span>
                </td>
                <td class="cell-split">
                    <input name="card-phone" type="number" value="<%= card_owner.phone %>" class="form-control w200">
                </td>
            </tr>
            <tr class="modify-card-name-tr">
                <td width="100" align="right" class="form-cell" valign="top">
                    <span class="text-muted">姓名</span>
                </td>
                <td class="cell-split">
                    <input name="card-name" value="<%= card_owner.name %>" class="form-control w200">
                </td>
            </tr>
        </table>
    </div>
</script>

<script type="text/template" name="card_search_box_template">
    <div class="form-group clearfix">
        <div class="col-xs-2">
            <select class="form-control search-card-type">
                <option value="" <%=card_type_selected==""?"selected":""%>>卡类型</option>
                <option value="5" <%=card_type_selected=="5"?"selected":""%>>业主卡</option>
                <option value="1" <%=card_type_selected=="1"?"selected":""%>>物业卡</option>
            </select>
        </div>
        <div class="col-xs-2">
            <select class="form-control search-card-status">
                <option value="" <%=card_status_selected==""?"selected":""%>>卡状态</option>
                <option value="1" <%=card_status_selected=="1"?"selected":""%>>使用中</option>
                <option value="2" <%=card_status_selected=="2"?"selected":""%>>注销中</option>
                <option value="3" <%=card_status_selected=="3"?"selected":""%>>已注销</option>
                <option value="4" <%=card_status_selected=="4"?"selected":""%>>激活中</option>
            </select>
        </div>
        <div class="col-xs-2">
            <select class="form-control search-card-group">
                <option value="">组团</option>
                <% for(var i=0;i<group_list.length;i++) { %>
                    <option value="<%= group_list[i] %>" <%= group_list[i]==group_selected ? "selected" : ""%>>
                        <%= group_list[i] %>
                    </option>
                <% } %>
            </select>
        </div>
        <div class="col-xs-2">
            <select class="form-control search-card-build">
                <option value="">楼栋</option>
                <% for(var i=0;i<build_list.length;i++) { %>
                    <option value="<%= build_list[i] %>" <%= build_list[i]==build_selected ? "selected" : ""%>>
                        <%= build_list[i] %>
                    </option>
                <% } %>
            </select>
        </div>
        <div class="col-xs-2">
            <select class="form-control search-card-unit">
                <option value="">单元</option>
                <% for(var i=0;i<unit_list.length;i++) { %>
                    <option value="<%= unit_list[i] %>" <%= unit_list[i]==unit_selected ? "selected" : ""%>>
                        <%= unit_list[i] %>
                    </option>
                <% } %>
            </select>
        </div>
        <div class="col-xs-2">
            <select class="form-control search-card-room">
                <option value="">房间</option>
                <% for(var i=0;i<room_list.length;i++) { %>
                    <option value="<%= room_list[i] %>" <%= room_list[i]==room_selected ? "selected" : ""%>>
                        <%= room_list[i] %>
                    </option>
                <% } %>
            </select>
        </div>
    </div>
    <div class="form-group clearfix">
        <div class="col-xs-2 brake_card_count"></div>
    </div>
</script>

<script type="text/template" name="card_list_template">
    <table class="table table-hover">
        <thead>
            <tr>
                <th><span class="text-muted">卡号</span></th>
                <th><span class="text-muted">社区</span></th>
                <th><span class="text-muted">组团</span></th>
                <th><span class="text-muted">楼栋</span></th>
                <th><span class="text-muted">单元</span></th>
                <th><span class="text-muted">房号</span></th>
                <th><span class="text-muted">有效期</span></th>
                <th><span class="text-muted">姓名</span></th>
                <th><span class="text-muted">通行时间</span></th>
                <th><span class="text-muted">通行位置</span></th>
                <th><span class="text-muted">类型</span></th>
                <th><span class="text-muted">状态</span></th>
                <th><span class="text-muted">可通行门禁</span></th>
                <th class="check-usertype"><center><span class="text-muted">操作</span></center></th>
            <tr>
        </thead>
        <tbody>
            <% for (var i=0; i<list.length; i++) {
                var item = list[i];
                var card_types={"1":"物业卡", "2":"组团卡", "3":"楼栋卡", "4":"单元卡", "5":"业主卡"};
                var card_status={"1":"使用中", "2":"注销中", "3":"已注销", "":"激活中"};
            %>
                <tr class="card-item" data-card-id="<%= item.id %>">
                    <td><%=item.card_no %> </td>
                    <td><%=_.pluck(item.card_area, 'project').join("<br/>")%> </td>
                    <td><%=_.pluck(item.card_area, 'group').join("<br/>")%> </td>
                    <td><%=_.pluck(item.card_area, 'build').join("<br/>")%> </td>
                    <td><%=_.pluck(item.card_area, 'unit').join("<br/>")%> </td>
                    <td><%=_.pluck(item.card_area, 'room').join("<br/>")%> </td>
                    <td>
                        <span>
                            <%= /4294967295/.test(item.card_validity) ? "永久" : new Date(item.card_validity * 1000).format("yyyy-MM-dd hh:mm:ss") %>
                        </span>
                    </td>
                    <td><%=item.card_owner.name %></td>
                    <td><%=item.updated_time %></td>
                    <td><%=item.recently_pass_position %></td>
                    <td><span><%=card_types[item.card_type] || item.card_type %></span></td>
                    <td><%=card_status[item.status] || "激活中" %> </td>
                    <td>
                        <%for(j=0;j<item.can_open_door_list.length;j++) {%>
                            <%=item.can_open_door_list[j] %>
                            <br>
                        <% } %>
                    </td>
                    <td class="check-usertype" align="center">
                        <a class="site-a edit-card-btn" href="javascript:void(0);">
                            <i class="fa fa-edit text-muted"></i>
                        </a>
                    </td>
                </tr>
            <% } %>
        </tbody>
    </table>
</script>