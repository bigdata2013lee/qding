<script type="text/template" name="view_template">
	<div>

		<h4>管理/房屋管理</h4>
		<div class="query_box" data-template="query_box">

			<form class="form-inline phase_build_select" role="form">
				<div class="form-group">
					<label class="control-label">组团/期</label>
					<input type="number" name="phase_no" class="form-control" min="1" placeholder="请输入组团/期" />
				</div>

				<div class="form-group">
					<label class="control-label">楼栋</label>
					<input type="number" name="building_no" class="form-control" min="1" placeholder="请输入楼栋" />
				</div>

				<div class="form-group">
					<label class="control-label">房间码</label>
					<input name="aptm_short_code" class="form-control" placeholder="请输入房间码" />
				</div>

				<button type="button" class="btn btn-primary query_btn"> 查询 </button>
				<a href="#AddHouse" data-toggle="modal" style="float: right;" ><button type="button" class="btn btn-primary query_btn"> 添加房屋 </button></a>
			</form>

		</div>

		<div class="data_list_box" data-template="aptm_list"></div>

	</div>
	<div class="modal fade" id="AddHouse" tabindex="-1" role="dialog" data-keyboard="true" data-backdrop="static">
		<div class="modal-dialog modal-lg" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title">添加房屋</h4>
				</div>
				<div class="modal-body submit_box" data-template="residents_window_body">
					<form class="form" id="AddHouse_input" role="form" style="margin-top: 0em;">
						<div class="form-group">
							<label class="control-label">组团/期</label>
							<input type="number" name="phase_no" class="form-control" min="1" placeholder="请输入组团/期" />
						</div>

						<div class="form-group">
							<label class="control-label">楼栋</label>
							<input type="number" name="building_no" class="form-control" min="1" placeholder="请输入楼栋" />
						</div>

						<div class="form-group">
							<label class="control-label">单元</label>
							<input type="number" class="form-control" name="unit_no" max="10" min="1">
						</div>

						<div class="form-group">
							<label class="control-label">楼层</label>
							<input name="floor_no" class="form-control" type="number" max="99" min="1" />
						</div>

						<div class="form-group">
							<label class="control-label">房号</label>
							<input name="room_no" class="form-control" type="number" max="10" min="0" />
						</div>

						<div class="form-group">
							<button type="button" class="btn btn-primary AddHouse_btn">保 存</button>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade" id="residents_window" tabindex="-1" role="dialog" data-keyboard="true" data-backdrop="static">
		<div class="modal-dialog modal-lg" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel2">住户</h4>
				</div>
				<div class="modal-body" data-template="residents_window_body">
					loading...
				</div>
			</div>
		</div>
	</div>

</script>

<script type="text/template" name="aptm_list_template">
	<table class="table table-striped table-hover">
		<thead>
			<tr>
				<th width="200px">房间</th>
				<th></th>
				<!--<th></th>-->
			</tr>
		</thead>

		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>" data-master="<%=item.master%>" data-talk_contact_phone="<%=item.talk_contact_phone%>">
				<td>
					<%=item.pre_names[1]%>
					<%=item.pre_names[2]%>
					<%=item.name%>
				</td>
				<td style="text-align: right;padding-right: 50px;">
					<a href="#residents_window" class="residents_window_btn" data-toggle="modal">住户管理</a>
					
				</td>
				<td>
					<a  href="#" class="deleteHouse" data-toggle="modal">删除</a>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>
	<%=qd.mk_pagination(data.pagination)%>
</script>

<script type="text/template" name="residents_window_body_template">
	<div class="part0">
		<h3><%=pre_names[1]%><%=pre_names[2]%><%=name%></h3>
	</div>
	<div class="part1" style="margin-top: 2em;">

		<form class="form-inline" role="form">
			<input type="hidden" type="hidden" name="aptm_id" value="<%=id%>" />
			<div class="input-group col-sm-4">
				<label class="sr-only"></label>
				<input type="text" name="mobile" class="form-control" placeholder="手机号码" maxlength="11" />
			</div>
			<div class="input-group">
				<label class="sr-only"></label>
				<button class="btn btn-primary bind_aptm_btn" type="button">绑定住户</button>
			</div>
		</form>
	</div>

	<div class="part2" data-template="residents" style="margin-top: 2em;">resident list</div>
	<div class="part1" style="margin-top: 2em; margin-bottom: 1em;">
		当前房间转接电话: <span class="connect_tel_box" data-template="connect_tel"></span>
	</div>
	<div class="input-group col-sm-4" style="margin-left: 10px; float: left;">
		<label class="sr-only"></label>
		<input type="text" name="phone_number" class="form-control" placeholder="转接号码" maxlength="11" />
	</div>
	<div class="input-group">
		<label class="sr-only"></label>
		<button class="btn btn-primary bind_talk_connect_tel_btn" style="margin-left: 5px;" type="button">设置转接电话</button>
	</div>
</script>

<script type="text/template" name="connect_tel_template">
	<span id="talk_connect_tel"><%= data.talk_contact_phone %></span>&nbsp;&nbsp;
	<% if( data.talk_contact_phone ) {%>
	<a href="javascript:" id="remove_connect_tel"><i class="glyphicon glyphicon-remove"></i></a>
	<% }%>
</script>

<script type="text/template" name="residents_template">

	<table class="table table-striped table-hover">
		<thead>

			<tr>
				<th width="120px">手机号</th>
				<th>名称</th>
				<th>家庭管理员</th>
				<th width="140px">注册时间</th>
				<th width="50px"></th>
				<th width="100px"></th>
			</tr>
		</thead>

		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=item.mobile%>
				</td>
				<td>
					<%=item.name%>
				</td>
				<td>
					<%if(sessionStorage.master === item.id){%><i class="glyphicon glyphicon-ok" style="color: green"></i>
					<%}%>
				</td>
				<td>
					<%=new Date(item.created_at).format('yyyy/MM/dd hh:mm')%>
				</td>
				<td>
					<a href="javascript:" class="unbind_aptm_btn" style="color: #d9534f;">解绑</a>
				</td>
				<td>
					<%if(sessionStorage.master !== item.id){%>
					<a href="javascript:" class="admin_aptm_btn" style="color: #449d44;">设置管理员</a>
					<%}%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>

</script>