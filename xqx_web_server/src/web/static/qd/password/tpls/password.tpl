<script type="text/template" name="view_template">
    <div>
        <h4>设置/修改密码</h4>
        <div class="submit_box" style="width: 600px;margin: 5em auto 0;">
            <form class="form phase_build_select" role="form" style="margin-top: 0em;width: 400px;">
                <div class="form-group">
                    <label class="control-label">旧密码*</label>
                    <input type="password" class="form-control" style="height: 45px;" name="old_password"/>
                </div>

                <div class="form-group">
                    <label class="control-label">新密码*</label>
                    <input type="password" class="form-control" style="height: 45px;"  name="new_password" placeholder="请输入四位以上密码"/>
                </div>

                <div class="form-group">
                    <label class="control-label">确认密码*</label>
                    <input type="password" class="form-control" style="height: 45px;"  name="confirm_passwd" placeholder="请输入四位以上密码"/>
                </div>

                <div class="form-group" style="    text-align: center;">
                    <button type="button" style="width: 111px;height: 43px;" class="btn btn-primary submit_btn">保 存</button>
                </div>
            </form>
        </div>
    </div>
</script>