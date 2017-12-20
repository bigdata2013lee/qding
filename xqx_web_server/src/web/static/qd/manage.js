
(function ($) {

    $(document).ready(function () {

        var initView=function(viewCls){
            if(app_router.view && app_router.view.destroy){
                app_router.view.destroy();
            }
            app_router.view  = new viewCls();
        };

        var routes = {
            'system/upgrade': function () {
                initView(qd.views.upgrade.MainView);
            },
            'agw/upgrade': function () {
                initView(qd.views.upgrade.AgwUpgradeView);
            },
            'qd/project': function () {
                initView(qd.views.project.ProjectView);
            },
            'setting/modify_passwd': function () {
                initView(qd.views.setting.ModifyPasswdView);
            },
            'setting/password': function () {
                initView(qd.views.project.password);
            },
            'qd/Advertisement':function(){
            	initView(qd.views.project.Advertisement)
            },
            '': function () {
                initView(qd.views.upgrade.MainView);
            }
        };

        var AppRouter = Backbone.Router.extend({
            content: '#page_content',
            view: null,
            routes: routes,
            defaultRoute : function(actions){
                initView(qd.views.dashborad.DashboradView);
            }
        });

        window.app_router = new AppRouter();
        Backbone.history.start();

    });

})(jQuery);
