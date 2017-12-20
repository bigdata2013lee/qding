<script type="text/template" name="view_template">
    <div>
        <h4>管理/添加房屋</h4>
        <div class="submit_box" style="width: 600px;margin: 5em auto 0;">
            <form class="form phase_build_select" role="form" style="margin-top: 0em;">
                <div class="form-group">
                    <label class="control-label">组团/期</label>
                     <input type="number" name="phase_no" class="form-control" min="1" placeholder="请输入组团/期"/>
                </div>

                <div class="form-group">
                    <label class="control-label">楼栋</label>
                   <input type="number" name="building_no" class="form-control" min="1" placeholder="请输入楼栋"/>
                </div>

                <div class="form-group">
                    <label class="control-label">单元</label>
                    <input type="number" class="form-control" name="unit"  max="10" min="1">
                </div>

                <div class="form-group">
                    <label class="control-label">楼层</label>
                    <input name="floor" class="form-control" type="number" max="99" min="1"/>
                </div>

                <div class="form-group">
                    <label class="control-label">房号</label>
                    <input name="room" class="form-control" type="number" max="10" min="0"/>
                </div>

                <div class="form-group">
                    <button type="button" class="btn btn-primary submit_btn">保 存</button>
                </div>
            </form>
        </div>
    </div>
</script>