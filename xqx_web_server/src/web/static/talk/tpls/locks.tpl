<script type="text/template" name="view_template">
	<div>

		<h4>对讲/开锁记录</h4>
		<div class="query_box" data-template="query_box">

			<form class="form-inline phase_build_select" role="form">
				<div class="form-group" style="margin-right: 20px;">
					<label class="control-label">类型</label>
					<select name="cls_name" class="form-control">
						<option value="">请选择开锁人类型</option>
						<option value="ResidentOpenLockRecord">住户</option>
						<option value="NotResidentOpenLockRecord">非住户</option>
					</select>
				</div>

				<button type="button" class="btn btn-primary query_btn"> 查询 </button>
			</form>

		</div>

		<div class="data_list_box" data-template="calls_list"></div>

	</div>
</script>

<script type="text/template" name="calls_list_template">
	<table style="text-align: center;" class="table table-striped table-hover">
		<thead>
			<tr>
				<th style="text-align: center;">门口机</th>
				<th style="text-align: center;">开锁人详情</th>
				<th style="text-align: center;">开锁方式</th>
				<th style="text-align: center;">开锁时间</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i]; %>
			<tr data-oid="<%=item.id%>">
				<td>
					<%=item.gate_name%>
				</td>
				<td>
					<%=item.opener_detail%>
				</td>
				<!-- <td><%=item.open_way%></td>-->
				<%= item.open_way === 'aptm_call' ? "<td>呼叫</td>" :"" %>
				<%=  item.open_way==='gate_pwd'? "<td>门口机密码</td>" :"" %>
				<%=  item.open_way==='app_remote'? "<td>APP远程</td>" :"" %>
				<%=  item.open_way==='card'? "<td>门卡</td>" :"" %>
				<%=  item.open_way==='resident_pwd '? "<td>输入密码</td>" :"" %>
				
				<td>
					<%=new Date(item.created_at).format('yyyy/MM/dd hh:mm')%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>
	<%=qd.mk_pagination(data.pagination)%>
</script>