<script type="text/template" name="data_list_table_template">
	<table class="table table-hover table-striped">
		<thead>
			<tr>
				<th style="width:30px"></th>
				<th style="width: 120px">类型</th>
				<th>程序包</th>
				<th>版本</th>
				<th>文件名</th>
				<th style="width: 180px">发布时间</th>
				<th>操作</th>
			</tr>
		</thead>
		<tbody>
			<% for(var i=0; i<data.collection.length; i++){ var item = data.collection[i];%>
			<tr data-oid="<%=item.id%>">
				<td>
					<%if(item.new_fg){%><i class="glyphicon glyphicon-ok" style="color: green"></i>
					<%}%>
				</td>
				<td>
					<%= item.component_type %>
				</td>
				<td>
					<%= item.name %>
				</td>
				<td>
					<%= item.version %>
				</td>
				<td>
					<%= item.filename %>
				</td>
				<td>
					<%= new Date(item.created_at).format("yyyy/MM/dd hh:mm") %>
					<%if(item.delay > 0){%>
					<br/><span style="color: #aaa;"> (离发布时间<%= item.delay%>小时后生效)</span>
					<%}%>
				</td>
				<td>
					<%if(item.release_status =="releaseing"){%>
					<a href="javascript:" class="deletePackage">停用</a>
					<%}%>
				</td>
			</tr>
			<%}%>
		</tbody>
	</table>

	<%=qd.mk_pagination(data.pagination)%>
</script>