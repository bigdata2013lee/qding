<script type="text/template" name="view_template">
	<div>
		<h4>社区管理/社区列表</h4>
		<div class="query_box" data-template="query_box">
			<form class="form-inline phase_build_select" role="form">
				<div class="form-group">
					<label class="control-label">省份</label>
					<select name="pcity_id" class="form-control"></select>
				</div>&nbsp;&nbsp;
				<div class="form-group">
					<label class="control-label">城市</label>
					<select name="ccity_id" class="form-control"></select>
				</div>&nbsp;&nbsp;
				<div class="form-group">
					<label class="control-label">社区名称</label>
					<input name="name_like" class="form-control" placeholder="请输入社区名称">
				</div>&nbsp;&nbsp;

				<button type="button" class="btn btn-primary query_btn"> 查询 </button>
				<button type="button" class="btn btn-primary add_project" data-toggle="modal" data-target="#add_project_window">
                        创建社区
                   </button>
                   	<button type="button" class="btn btn-primary add_project" data-toggle="modal" data-target="#add_project_window">
                        查看已删除社区
                   </button>
			</form>
		</div>

		<div class="data_list_box" data-template="projects"></div>
		<div class="modal fade" id="add_project_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
			<div class="modal-dialog" role="document">
				<div class="modal-content add_project">
					<div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                                aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="myModalLabel1">创建社区</h4>
					</div>
					<div class="modal-body projects">
						<form class="form-horizontal" id="projects_form">

							<div class="form-group">
								<label class="col-sm-2 control-label">省份</label>
								<div class="col-sm-10">
									<select name="pcity_id" class="form-control Province"></select>
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">城市</label>
								<div class="col-sm-10">
									<select name="ccity_id" class="form-control City"></select>
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">街道</label>
								<div class="col-sm-10">
									<input type="text" name="street" class="form-control" placeholder="" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">社区名称</label>
								<div class="col-sm-10">
									<input type="text" name="project_name" class="form-control" placeholder="" />
								</div>
							</div>
						</form>
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-primary sumbit_btn_add_project">保 存</button>
					</div>
				</div>
			</div>
		</div>
		<div class="modal fade" id="Administrators">
			<div class="modal-dialog" role="document">
				<div class="modal-content modify">
					<div class="modal-body projects">
						<div class="data_msg_box" data-template="create_projects_msg"></div>
					</div>
				</div>
			</div>
		</div>
	</div>
</script>

<script type="text/template" name="create_projects_msg_template">
	<pre style="margin: 10px;">社区: <%=Province%><%=City%><%=street%><%=data.project_name%> </pre>
	<pre style="margin: 10px;">当前社区管理员帐号/密码: <%=data.project_code%> / <%=data.init_pwd%></pre>
</script>

<script type="text/template" name="projects_template">
	<table class="table table-hover table-striped">
		<thead>
			<tr>
				<th>社区编码</th>
				<th>社区名称</th>
				<th>省/市</th>
				<th>街道</th>
				<th>操作</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>" data-code="<%=item.code%>" data-name="<%=item.name%>" data-label="<%=item.label%>" data-street="<%=item.ccity_name%>">
				<td>
					<%=item.code%>
				</td>
				<td>
					<%=item.name%>
					<% if(item.label) { %> (
					<%=item.label %>)
					<% } %>
				</td>
				<td>
					<%=item.ccity_name%>
				</td>
				<td>
					<%=item.street%>
				</td>
				<td>
					<a href="#import_aptm_window" class="aptm_modal" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-import" aria-hidden="true"></span>房屋导入</a>&nbsp;&nbsp;&nbsp;
					<!--                <a href="#import_aptm_window" class="aptm_modal" style="color:#3399CC" data-code="<%=item.code%>" data-toggle="modal"><span class="glyphicon glyphicon-search" aria-hidden="true"></span>查看</a>&nbsp;&nbsp;&nbsp;-->
					<a href="#modify_info_window" class="modify_modal modifylist" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-cog " aria-hidden="true"></span>修改</a>&nbsp;&nbsp;&nbsp;
					<a href="#" class="reset_passwd" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-console" aria-hidden="true"></span>重置密码</a>&nbsp;&nbsp;&nbsp;
					<a href="#" class="remove_project" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span>删除</a>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>
	<%=qd.mk_pagination(data.pagination)%>
	<div class="modal fade bs-example-modal-sm" id="import_aptm_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel4">
		<div class="modal-dialog" role="document">
			<div class="modal-content import">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel4">批量导入房屋</h4>
					<div class="progress" style="display: none;margin: 0;">
						<div class="progress-bar progress-bar-info progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;" id="percent">
							<span></span>
						</div>
					</div>
				</div>
				<div class="modal-body">
					<form class="form-horizontal" id="import_aptm_window_form">
						<input type="hidden" name="project_id">
						<div class="form-group">
							<label class="col-sm-2 control-label">csv文件</label>
							<div class="col-sm-10">
								<input type="file" name="csv_file" />
							</div>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary sumbit_btn">导入文件</button>
				</div>
				<pre id="errorInfo" style="margin: 10px;display: none;"></pre>
			</div>
		</div>
	</div>

	<div class="modal fade" id="modify_info_window">
		<div class="modal-dialog modify_project" role="document">
			<div class="modal-content modify">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                            aria-hidden="true">&times;</span></button>
					<h4 class="modal-title">社区信息修改</h4>
				</div>
				<div class="modal-body projects">
					<form class="form-horizontal" id="info_form">
						<div class="form-group">
							<label class="col-sm-2 control-label">社区编号</label>
							<div class="col-sm-10">
								<input type="hidden" name="project_id" class="form-control" value="" />
								<input type="text" name="project_code" class="form-control projectcode" readonly  />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">社区名称</label>
							<div class="col-sm-10">
								<input type="text" name="name" class="form-control" placeholder="" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">标签</label>
							<div class="col-sm-10">
								<input type="text" name="label" class="form-control" placeholder="" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">街道</label>
							<div class="col-sm-10">
								<input type="text" name="street" class="form-control" placeholder="" />
							</div>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">取消</button>
					<button type="button" class="btn btn-primary sumbit_btn">保 存</button>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade" id="reset_passwd_window">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>
					<h4 class="modal-title">重置密码</h4>
				</div>
				<div class="modal-body">
					<h5 class="modal-title">项目名称：</h5>
					<div class="alert alert-success" role="alert" id="project_name"></div>
				</div>
				<div class="modal-body">
					<h5 class="modal-title">项目编号：</h5>
					<div class="alert alert-success" role="alert" id="project_code"></div>
				</div>
				<div class="modal-body">
					<h5 class="modal-title">管理员帐号/密码：</h5>
					<div class="alert alert-success" role="alert" id="init_pwd"></div>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary" data-dismiss="modal">关闭</button>
				</div>
			</div>
		</div>
	</div>
</script>