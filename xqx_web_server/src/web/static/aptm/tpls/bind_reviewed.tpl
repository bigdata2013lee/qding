<script type="text/template" name="view_template">
    <div>
        <h4>管理/绑定审批</h4>
        <div class="query_box" data-template="query_box">
            <form class="form-inline phase_build_select" role="form">
                <div class="form-group">
                    <label class="control-label">审批状态</label>
                    <select name="status" class="form-control">
                        <option value="">全部</option>
                        <option value="new">未审核</option>
                        <option value="pass">通过</option>
                        <option value="reject">拒绝</option>
                    </select>
                </div>
                <button type="button" class="btn btn-primary query_btn"> 查询 </button>
            </form>
        </div>

        <div class="data_list_box" data-template="reviewed"></div>

        <div class="modal fade" id="log_window">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                        <h4 class="modal-title">查看备注信息</h4>
                    </div>
                    <div class="modal-body">
                        <h5 class="modal-title">申请备注</h5>
                        <div class="alert alert-success" role="alert" id="user_notice">暂无信息</div>

                        <h5 class="modal-title">审核备注</h5>
                        <div class="alert alert-info" role="alert" id="wy_notice">暂无信息</div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-default" data-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="modal fade" id="reject_window">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
                        <h4 class="modal-title">确定要拒绝申请?</h4>
                    </div>
                    <div class="modal-body">
                        <textarea name="" id="wy_notice_txt" class="form-control" rows="3" placeholder="请输入审核原因"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-default" data-dismiss="modal">取消</button>
                        <button type="button" class="btn btn-primary reject-submit">确定</button>
                    </div>
                </div>
            </div>
        </div>

</script>

<script type="text/template" name="reviewed_template">
    <table class="table table-hover table-striped">
        <thead>
            <tr>
                <th>申请时间</th>
                <th>申请手机</th>
                <th>申请房号</th>
                <th>申请备注</th>
                <th>申请/审核备注</th>
                <th>当前状态</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
            <tr data-oid="<%=item.id%>">
                <td><%=new Date(item.created_at).format('yyyy/MM/dd hh:mm:ss') %></td>
                <td><%=item.user_mobile%></td>
                <td><%=item.target_aptm_name%></td>
                <td><%=item.user_notice%></td>
                <td><a href="javascript:" class="a-modal" style="color:#3399CC;" data-user-notice="<%=item.user_notice%>" data-wy-notice="<%=item.wy_notice%>">查看</a></td>
                <td><%=qd.choices.review_types[item.status]%></td>
                <td>
                    <% if(item.status === "new"){%>
                        <a href="javascript:" style="color:#449d44;" class="pass-btn">同意</a>
                        <a href="javascript:" style="color:#d9534f;" class="reject-btn">拒绝</a>
                    <% } %>
                </td>
            </tr>
            <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>

