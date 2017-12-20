<script type="text/template" name="view_template">
	<div>
		<h4>快捷入口</h4>
		<div class="btn-group btn-group-justified" role="group">
			<div class="btn-group">
				<button aria-expanded="false" style="font-size: 16px;height: 50px;" aria-haspopup="true" data-toggle="dropdown" class="btn btn-info dropdown-toggle" type="button">
                        <span>添加门卡</span>
                        <span class="caret"></span>
                    </button>
				<ul class="dropdown-menu dropdown-menu-right">
					<li>
						<a href="#add_resident_card_window" data-toggle="modal">业主卡</a>
					</li>
					<li>
						<a href="#add_manager_card_window" data-toggle="modal">物业卡</a>
					</li>
					<li>
						<a href="#add_worker_card_window" data-toggle="modal">工作卡</a>
					</li>
				</ul>
			</div>
			<div class="btn-group" role="group">
				<a href="#project/aptm">
				<button aria-expanded="false" style="height: 50px;margin-left: 20px; font-size: 16px;"  aria-haspopup="true"  class="btn btn-info dropdown-toggle" type="button">
                    <span>添加住户</span>
                    </button>
                     </a>
			</div>
			<div class="btn-group" role="group">
				<a href="#aptm/reviewed">
				<button aria-expanded="false" style="height: 50px;margin-left: 40px; font-size: 16px;"  aria-haspopup="true"  class="btn btn-info dropdown-toggle" type="button">
                    <span>新申请</span>
                    </button>
                    </a>
			</div>
		</div>
	</div>
	<div>
		<h4>统计监控</h4>
		<div class="pull-left col-xs-7">
			<div class="alarm_list_box" data-template="alarm_list"></div>
			<div class="recent_alarm_list_box" data-template="recent_alarm_list"></div>
		</div>
		<div class="pull-right col-xs-5">

			<div class="device_status_list_box" data-template="device_status_list"></div>

			<div>
				<pre><strong>近期离线设备</strong></pre>
				<div>
					<div class="bs-example bs-example-tabs">
						<ul id="myTab" class="nav nav-tabs" role="tablist">
							<li role="presentation" class="active">
								<a href="#home" id="home-tab" role="tab" data-toggle="tab" aria-controls="home" aria-expanded="true">门口机</a>
							</li>
							<li role="presentation">
								<a href="#dropdown1" role="tab" id="profile-tab1" data-toggle="tab" aria-controls="profile">报警网关</a>
							</li>
							<li role="presentation">
								<a href="#dropdown2" role="tab" id="profile-tab2" data-toggle="tab" aria-controls="profile">管理中心机</a>
							</li>
						</ul>
						<div id="myTabContent" class="tab-content">
							<div role="tabpanel" class="tab-pane fade in active gates_list_box" id="home" aria-labelledby="home-tab" data-template="gates_list"></div>
							<div role="tabpanel" class="tab-pane fade agws_list_box" id="dropdown1" aria-labelledby="dropdown1-tab" data-template="agws_list"></div>
							<div role="tabpanel" class="tab-pane fade aios_list_box" id="dropdown2" aria-labelledby="dropdown1-tab" data-template="aios_list"></div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade" id="add_resident_card_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                            aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel1">添加门禁卡</h4>
				</div>
				<div class="modal-body">
					<form class="form-horizontal">
						<div class="form-group">
							<label class="col-sm-2 control-label">组团/期</label>
							<div class="col-sm-10">
								<input type="number" name="phase" class="form-control" placeholder="组团/期" max="10" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">楼栋</label>
							<div class="col-sm-10">
								<input type="number" name="build" class="form-control" placeholder="楼栋" max="200" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">单元</label>
							<div class="col-sm-10">
								<input type="number" name="unit" class="form-control" placeholder="单元" max="10" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">楼层</label>
							<div class="col-sm-10">
								<input type="number" name="floor" class="form-control" placeholder="楼层" max="60" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">房间</label>
							<div class="col-sm-10">
								<input type="number" name="room" class="form-control" placeholder="房间" max="40" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">卡号</label>
							<div class="col-sm-10">
								<input name="card_no" class="form-control accept_car_reader multi" placeholder="卡号, 多个卡用逗号(,)分隔 " />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">有效期</label>
							<div class="col-sm-10  has-feedback date up">
								<input name="expiry_date" class="form-control" placeholder="不输入为长期有效 " />
								<span class="form-control-feedback add-on" aria-hidden="true">
                                    <i class="icon-calendar"></i>
                                </span>
							</div>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary sumbit_btn"> 保存</button>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade" id="add_manager_card_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                            aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel2">添加物业门禁卡</h4>
				</div>
				<div class="modal-body">
					<form class="form-horizontal">
						<div class="form-group">
							<label class="col-sm-2 control-label">姓名</label>
							<div class="col-sm-10">
								<input type="text" name="owner_name" class="form-control" placeholder="姓名" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">卡号</label>
							<div class="col-sm-10">
								<input type="number" name="card_no" class="form-control accept_car_reader" placeholder="卡号" max="999999999" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">有效期</label>
							<div class="col-sm-10  has-feedback date down" data-picker_position="bottom-left">
								<input name="expiry_date" class="form-control" placeholder="不输入为长期有效 " />
								<span class="form-control-feedback add-on" aria-hidden="true">
                                    <i class="icon-calendar"></i>
                                </span>
							</div>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary sumbit_btn"> 保存</button>
				</div>
			</div>
		</div>
	</div>
	<div class="modal fade" id="add_worker_card_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                            aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel3">添加工作门禁卡</h4>
				</div>
				<div class="modal-body">
					<form class="form-horizontal">
						<div class="form-group">
							<label class="col-sm-2 control-label">姓名</label>
							<div class="col-sm-10">
								<input type="text" name="owner_name" class="form-control" placeholder="姓名" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">卡号</label>
							<div class="col-sm-10">
								<input type="number" name="card_no" class="form-control accept_car_reader" placeholder="卡号" max="999999999" min="1" />
							</div>
						</div>
						<div class="form-group">
							<label class="col-sm-2 control-label">有效期</label>
							<div class="col-sm-10  has-feedback date down" data-picker_position="bottom-left">
								<input name="expiry_date" class="form-control" placeholder="不输入为长期有效 " />
								<span class="form-control-feedback add-on" aria-hidden="true">
                                    <i class="icon-calendar"></i>
                                </span>
							</div>
						</div>
					</form>
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary sumbit_btn"> 保存 </button>
				</div>
			</div>
		</div>
	</div>
	<!--<div class="modal fade" id="add_worker_card_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
		<div class="modal-dialog" role="document">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span
                            aria-hidden="true">&times;</span></button>
					<h4 class="modal-title" id="myModalLabel3">添加住户</h4>
				</div>
				<div class="modal-body">
					
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-primary sumbit_btn"> 保存 </button>
				</div>
			</div>
		</div>
	</div>-->
</script>

<script type="text/template" name="alarm_list_template">
	<table class="table table-hover">
		<pre><strong>报警统计(最近7天)</strong></pre>
		<thead>
			<tr>
				<th>类型</th>
				<th>报警次数</th>
				<th>已处理</th>
				<th>未处理</th>
			</tr>
		</thead>
		<tbody>

			<% if(JSON.stringify(data.stt_categorys) === "{}"){%>
			<tr>
				<td class="time" style="text-align: center" colspan="4">暂无数据</td>
			</tr>
			<%  }%>

			<% for(var i=1; i<8; i++){ var item = data.stt_categorys[i]; %>
			<% if(item){%>
			<tr>
				<td>
					<%=qd.choices.alarm_types[i] %>
				</td>
				<td>
					<%=item[0]%>
				</td>
				<td><span class="f1"><%=item[1] %> </span></td>
				<td><span class="f2"><%= item[2] %></span></td>
			</tr>
			<%}}%>
		</tbody>
	</table>

</script>

<script type="text/template" name="recent_alarm_list_template">
	<table class="table table-hover">
		<pre><strong>最近报警记录</strong></pre>
		<thead>
			<tr>
				<th>类型</th>
				<th>描述</th>
			</tr>
		</thead>
		<tbody>
			<% if(data.collection.length === 0){%>
			<tr>
				<td class="time" style="text-align: center" colspan="3">暂无数据</td>
			</tr>
			<% }%>

			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=qd.choices.alarm_types[item.alarm_type]%>报警</td>
				<td>
					<%=item.name%>
				</td>
			</tr>
			<%}%>

		</tbody>
	</table>

</script>

<script type="text/template" name="device_status_list_template">
	<table class="table table-hover">
		<pre><strong>设备状态</strong></pre>
		<thead>
			<tr>
				<th>设备名称</th>
				<th>设备数</th>
				<th>在线</th>
				<th>离线</th>
			</tr>
		</thead>
		<tbody>
			<tr>
				<td>
					<%=qd.choices.device_types['AioManager']  %>
				</td>
				<td>
					<%=data.AioManager.all%>
				</td>
				<td><span class="f1"><%=data.AioManager.online %></span></td>
				<td><span class="f2"> <%= data.AioManager.all - data.AioManager.online %></span></td>
			</tr>
			<tr>
				<td>
					<%=qd.choices.device_types['AlarmGateway']  %>
				</td>
				<td>
					<%=data.AlarmGateway.all%>
				</td>
				<td><span class="f1"><%=data.AlarmGateway.online %></span></td>
				<td><span class="f2"> <%= data.AlarmGateway.all - data.AlarmGateway.online %></span></td>
			</tr>
			<tr>
				<td>
					<%=qd.choices.device_types['FenceGate']  %>
				</td>
				<td>
					<%=data.FenceGate.all%>
				</td>
				<td><span class="f1"><%=data.FenceGate.online %> </span></td>
				<td><span class="f2"> <%= data.FenceGate.all - data.FenceGate.online %></span></td>
			</tr>
			<tr>
				<td>
					<%=qd.choices.device_types['UnitGate']  %>
				</td>
				<td>
					<%=data.UnitGate.all%>
				</td>
				<td><span class="f1"><%=data.UnitGate.online %> </span></td>
				<td><span class="f2"> <%= data.UnitGate.all - data.UnitGate.online %></span></td>
			</tr>
		</tbody>
		</tbody>
	</table>

</script>

<script type="text/template" name="gates_list_template">
	<table class="table table-hover">
		<thead>
			<tr>
				<th>设备</th>
				<th>心跳时间</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=item.name %>
				</td>
				<td>
					<%=new Date(item.heartbeat.at).format('yyyy/MM/dd hh:mm')%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>

</script>

<script type="text/template" name="agws_list_template">
	<table class="table table-hover">
		<thead>
			<tr>
				<th>设备</th>
				<th>心跳时间</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=item.aptm_name %>
				</td>
				<td>
					<%=new Date(item.heartbeat.at).format('yyyy/MM/dd hh:mm')%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>

</script>

<script type="text/template" name="aios_list_template">
	<table class="table table-hover">
		<thead>
			<tr>
				<th>设备</th>
				<th>心跳时间</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=item.name %>
				</td>
				<td>
					<%=new Date(item.heartbeat.at).format('yyyy/MM/dd hh:mm')%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>

</script>