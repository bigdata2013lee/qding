<script type="text/template" name="view_template">
    <div class="page-header clearfix">
        <b class="" style="font-size:18px;">基础数据 - 数据综览</b>
    </div>
    <div class="scan_data" data-template="scan_data"></div>
</script>

<script type="text/template" name="scan_data_template">
    <div class="form-horizontal" style="padding:20px 20px 5px 20px;background-color:#f7f8f9;">
    <div class="form-group">
        <div class="col-xs-12">
            <span class="col-xs-offset-1 col-xs-3">累计开门次数: <%=pass_count %>次</span>
            <div class="col-xs-3 open-door-count"></div>
        </div>
    </div>
    <div class="form-group">
        <div class="col-xs-12">
            <span class="col-xs-offset-1 col-xs-3">项目数量: <%=project_count %>个</span>
            <div class="col-xs-3 project-count"></div>
        </div>
    </div>
    <div class="form-group">
        <div class="col-xs-12">
            <span class="col-xs-offset-1 col-xs-3">门禁数量: <%=brake_machine_count %>台</span>
            <div class="col-xs-3 brake-machine-count"></div>
        </div>
    </div>
    </div>
</script>