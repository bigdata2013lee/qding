<style>
    div.form-group.apm_c input {max-width: 60px;}
</style>
<script type="text/template" name="view_template">
    <div class="card_page">
        <h4>管理/小区门卡</h4>
        <div class="query_box">

            <form class="form-inline pull-left">
                <div class="form-group">
                    <select class="form-control" name="card_type">
                        <option value="">-- 所有类型 --</option>
                        <option value="resident" selected>业主卡</option>
                        <option value="manager">物业卡</option>
                        <option value="worker">工作卡</option>
                    </select>
                </div>

                <div class="form-group like_input" style="display: none;">
                    <input type="text" class="form-control accept_car_reader" name="card_no_like" placeholder="请输入卡号"/>
                </div>

                <div class="form-group like_input" style="display: none;">
                    <input type="text" class="form-control" name="owner_name_like" placeholder="请输入持卡人"/>
                </div>

                <div class="form-group apm_c">
                    <div class="input-group">
                        <input name="phase" class="form-control" type="number" min="1" max="10" size="2"/>
                        <span class="input-group-addon">组团/期</span>
                    </div>
                </div>

                <div class="form-group apm_c">
                    <div class="input-group">
                        <input name="build" class="form-control" type="number" min="1" max="100"/>
                        <span class="input-group-addon">楼栋</span>
                    </div>
                </div>

                <div class="form-group apm_c">
                    <div class="input-group">
                        <input name="unit" class="form-control" type="number" min="1" max="10"/>
                        <span class="input-group-addon">单元</span>
                    </div>
                </div>

                <div class="form-group apm_c">
                    <div class="input-group">
                        <input name="floor" class="form-control" type="number" min="1" max="60"/>
                        <span class="input-group-addon">楼层</span>
                    </div>
                </div>

                <div class="form-group apm_c">
                    <div class="input-group">
                        <input name="room" class="form-control" type="number" min="1" max="12"/>
                        <span class="input-group-addon">房间</span>
                    </div>
                </div>

                <button type="button" class="btn btn-primary query_btn">查 询</button>

            </form>

            <div class="pull-right">

                <div class="btn-group">
                    <button aria-expanded="false" aria-haspopup="true" data-toggle="dropdown" class="btn btn-info dropdown-toggle" type="button">
                        <span>添加卡</span>
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-right">
                        <li><a href="#add_resident_card_window" data-toggle="modal">业主卡</a></li>
                        <li><a href="#add_manager_card_window" data-toggle="modal">物业卡</a></li>
                        <li><a href="#add_worker_card_window" data-toggle="modal">工作卡</a></li>
                    </ul>
                </div>

                <div class="btn-group">
                    <button aria-expanded="false" aria-haspopup="true" data-toggle="dropdown"
                            class="btn btn-default export_access_cards">
                        <span>更多</span>
                        <span class="caret"></span>
                    </button>

                    <ul class="dropdown-menu dropdown-menu-right">
                        <li><a href="#import_cards_window" data-toggle="modal">导入门禁卡</a></li>
                        <li><a href="/remote/card.ImportExportCardApi.export_cards/">导出门禁卡</a></li>
                    </ul>

                </div>
            </div>
            <br clear="both"/>


        </div>

        <div class="data_list_div">
            <center>正在加载...</center>
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
                                <input type="number" name="phase" class="form-control" placeholder="组团/期" max="10"
                                       min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">楼栋</label>
                            <div class="col-sm-10">
                                <input type="number" name="build" class="form-control" placeholder="楼栋" max="200"
                                       min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">单元</label>
                            <div class="col-sm-10">
                                <input type="number" name="unit" class="form-control" placeholder="单元" max="10"
                                       min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">楼层</label>
                            <div class="col-sm-10">
                                <input type="number" name="floor" class="form-control" placeholder="楼层" max="60"
                                       min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">房间</label>
                            <div class="col-sm-10">
                                <input type="number" name="room" class="form-control" placeholder="房间" max="40"
                                       min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">卡号</label>
                            <div class="col-sm-10">
                                <input name="card_no" class="form-control accept_car_reader multi"
                                       placeholder="卡号, 多个卡用逗号(,)分隔 "/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">有效期</label>
                            <div class="col-sm-10  has-feedback date up">
                                <input name="expiry_date" class="form-control" placeholder="不输入为长期有效 "/>
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
                                <input type="text" name="owner_name" class="form-control" placeholder="姓名"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">卡号</label>
                            <div class="col-sm-10">
                                <input type="number" name="card_no" class="form-control accept_car_reader"
                                       placeholder="卡号" max="999999999" min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">有效期</label>
                            <div class="col-sm-10  has-feedback date down" data-picker_position="bottom-left">
                                <input name="expiry_date" class="form-control" placeholder="不输入为长期有效 "/>
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
                                <input type="text" name="owner_name" class="form-control" placeholder="姓名"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">卡号</label>
                            <div class="col-sm-10">
                                <input type="number" name="card_no" class="form-control accept_car_reader"
                                       placeholder="卡号" max="999999999" min="1"/>
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="col-sm-2 control-label">有效期</label>
                            <div class="col-sm-10  has-feedback date down" data-picker_position="bottom-left">
                                <input name="expiry_date" class="form-control" placeholder="不输入为长期有效 "/>
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


    <div class="modal fade bs-example-modal-sm" id="import_cards_window" tabindex="-1" role="dialog" aria-labelledby="myModalLabel4">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                    <h4 class="modal-title" id="myModalLabel4">导入门禁卡</h4>
                    <div class="progress" style="display: none;margin: 0;">
                        <div class="progress-bar progress-bar-info progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0;" id="percent">
                            <span></span>
                        </div>
                    </div>
                </div>
                <div class="modal-body">
                    <form class="form-horizontal">
                        <div class="form-group">
                            <label class="col-sm-2 control-label">csv文件</label>
                            <div class="col-sm-10">
                                <input type="file" name="myfiles"/>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary sumbit_btn"> 导入文件</button>
                </div>
                <pre id="errorInfo" style="margin: 10px;display: none;"></pre>
            </div>
        </div>
    </div>
</script>


<script type="text/template" name="data_list_template">

    <table class="table table-striped table-hover">
        <thead>
        <tr>
            <th>类型</th>
            <th>卡号</th>
            <th>持卡人</th>
            <th>截止有效期</th>
            <th>操作</th>
        </tr>
        </thead>

        <tbody>
        <% for(var i=0; i<data.collection.length; i++){
        var item = data.collection[i];
        var card_types_map={'resident': '业主卡', 'manager': '物业卡', 'guest': '访客卡', 'worker': '工作卡'};
        %>
        <tr data-oid="<%=item.id%>">
            <td><%=card_types_map[item.card_type] || "" %></td>
            <td><%=item.card_no%></td>
            <td><%=item.owner_name%></td>
            <td><%=item.expiry_date>=7258089600000?"长期有效":new Date(item.expiry_date).format('yyyy/MM/dd')%></td>
            <td>
                <a href="javascript:" name="unregister_card"><i class="glyphicon glyphicon-remove"></i></a>
            </td>
        </tr>
        <%}%>
        </tbody>
    </table>
    <%=qd.mk_pagination(data.pagination)%>
</script>
