<script type="text/template" name="view_template">
	<div>
		<h4>广告管理</h4>
		<div class="query_box" data-template="query_box" style="padding-top: 0px;">
			<form class="form-inline phase_build_select" role="form">
				<button type="button" class="btn btn-primary add-project" data-toggle="modal" data-target="#EstablishAdvertList">
                        创建广告
                    </button>
				<!--<button type="button" style="float: right;" class="btn btn-primary add-project" data-toggle="modal" data-target="#">
                        查看历史记录
                    </button>-->

			</form>
			<!--<input type="button"  class="list_demo" />
			<ul id="list_test">
				
				</ul>-->
		</div>
		<div class="data_list_box" data-template="AdverList"></div>
		<div class="modal fade bs-example-modal-sm" id="EditStatus" tabindex="-1" role="dialog" aria-labelledby="myModalLabel4">
			<div class="modal-dialog" style="    margin-top: 182px;" role="document">
				<div class="modal-content import">
					<div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="myModalLabel4">编辑状态</h4>
						<div class="progress" style="display: none;margin: 0;">
							<div class="progress-bar progress-bar-info progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;" id="percent">
								<span></span>
							</div>
						</div>
					</div>
					<div class="modal-body">
						<form class="form-horizontal" id="edit_list">
							<div class="form-group">
								<label class="col-sm-2 control-label">广告范围</label>
								<div class="col-sm-10">
									<button type="button" class="btn btn-primary edit_PCityApi" data-toggle="modal" data-target="#editPCityApi">
                        选择范围
                    </button>
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">有效期</label>
								<div class="col-sm-10">
									<input type="text" style="width: 40%;    display: initial;" name="start_date" class="form-control startTime" placeholder="" /> 至
									<input type="text" style="width: 40%;    display: initial;" name="end_date" class="form-control endTime" placeholder="" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">权重倍数</label>
								<div class="col-sm-10">
									<div class="btn-group" role="group" aria-label="...">
										<select name="weight" class="form-control edit_weight">
											<option value="1">一倍</option>
											<option value="2">两倍</option>
											<option value="3">三倍</option>
										</select>
									</div>
								</div>
							</div>
						</form>
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-primary edit_but">保存</button>
					</div>
				</div>
			</div>
		</div>

		<div class="modal fade" id="EstablishAdvertList" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
			<div class="modal-dialog" role="document">
				<div class="modal-content add_project" style="margin-top: 105px;">
					<div class="modal-header">
						<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
						<h4 class="modal-title" id="myModalLabel1">创建广告</h4>
					</div>

					<div class="modal-body">

						<form class="form-horizontal" id="Advertesment_list">
							<div class="form-group">
								<label class="col-sm-2 control-label">视频或图片文件</label>
								<div class="col-sm-10">
									<input type="file" name="media_file" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">广告标题</label>
								<div class="col-sm-10">
									<input type="text" style="width: 85%;" name="adv_name" class="form-control company" placeholder="" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">有效期</label>
								<div class="col-sm-10">
									<input type="text" style="width: 40%;    display: initial;" name="start_date" class="form-control startTime" placeholder="" /> 至
									<input type="text" style="width: 40%;    display: initial;" name="end_date" class="form-control endTime" placeholder="" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">所属公司</label>
								<div class="col-sm-10">
									<input type="text" style="width: 85%;" name="company_name" class="form-control company" placeholder="" />
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">广告范围</label>
								<div class="col-sm-10">
									<button type="button" class="btn btn-primary add_PCityApi" data-toggle="modal" data-target="#PCityApi">
                        选择范围
                    </button>
								</div>
							</div>
							<div class="form-group">
								<label class="col-sm-2 control-label">权重倍数</label>
								<div class="col-sm-10">
									<div class="btn-group" role="group" aria-label="...">
										<select name="weight" class="form-control">
											<option value="1">一倍</option>
											<option value="2">两倍</option>
											<option value="3">三倍</option>
										</select>
									</div>
								</div>
							</div>
						</form>
					</div>

					<div class="modal-footer">
						<button type="button" class="btn btn-primary sumbit_btn">保 存</button>
					</div>
				</div>
			</div>
		</div>

</script>
<script type="text/template" name="AdverList_template">
	<table class="table table-hover table-striped">
		<thead>
			<tr>
				<th>名称</th>
				<!--<th>文件名</th>-->
				<th>类型</th>
				<th>开始日期</th>
				<th>结束日期</th>
				<th>所属公司</th>
				<th>操作</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">

				<td>
					<%=item.name%>
				</td>
				<!--<td>
					视频文件.jpg
				</td>-->
				<td>
					<%=item.adv_type%>
				</td>
				<td>
					<%=new Date(item.start_at).format('yyyy年MM月dd日')%>
				</td>
				<td>
					<%=new Date(item.end_at).format('yyyy年MM月dd日')%>
				</td>
				<td>
					<%=item.company_name%>
				</td>
				<td>
					<a href="#EditStatus" class="modify_modal" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-import" aria-hidden="true"></span>编辑</a>&nbsp;&nbsp;&nbsp;
					<a href="#" class="remove_project" style="color:#3399CC" data-toggle="modal"><span class="glyphicon glyphicon-remove" aria-hidden="true"></span>删除</a>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>
	<%=qd.mk_pagination(data.pagination)%>
	<div class="modal fade bs-example-modal-sm" style="z-index: 1051;" id="PCityApi" tabindex="-1" role="dialog" aria-labelledby="myModalLabel4">
		<div class="modal-dialog" style="    margin-top: 182px;" role="document">
			<div class="modal-content import">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel4">选择范围</h4>
					<div class="progress" style="display: none;margin: 0;">
						<div class="progress-bar progress-bar-info progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;" id="percent">
						</div>
					</div>
				</div>
				<div class="modal-body">
					<ul id="pcityApi_list" class="pcityApi">

					</ul>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary tree">保存</button>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade bs-example-modal-sm" style="z-index: 1051;" id="editPCityApi" tabindex="-1" role="dialog" aria-labelledby="myModalLabel4">
		<div class="modal-dialog" style="    margin-top: 182px;" role="document">
			<div class="modal-content import">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel4">选择范围</h4>
					<div class="progress" style="display: none;margin: 0;">
						<div class="progress-bar progress-bar-info progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;" id="percent">
						</div>
					</div>
				</div>
				<div class="modal-body">
					<ul id="editpcityApi_list" class="editpcityApi">

					</ul>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary editTree">保存</button>
				</div>
			</div>
		</div>
	</div>
</script>