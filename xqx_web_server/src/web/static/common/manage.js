
(function ($) {

    $(document).ready(function () {

        var initView=function(viewCls){
            if(app_router.view && app_router.view.destroy){
                app_router.view.destroy();
            }
            app_router.view  = new viewCls();
        };

        var routes = {
            'agw/device': function () {
                initView(qd.views.agw.DeviceView);
            },
            'agw/alarm': function () {
                initView(qd.views.agw.AlarmView);
            },
            'project/aptm': function () {
                initView(qd.views.project.AptmView);
            },
            'project/phase': function () {
                initView(qd.views.project.PhaseView);
            },
            'project/add_aptm': function () {
                initView(qd.views.project.AddAptmView);
            },
            'aptm/reviewed': function () {
                initView(qd.views.project.AptmBindReviewedView);
            },
            'aptm/help': function () {
                initView(qd.views.project.AptmTplsView);
            },
            'talk/gates': function () {
                initView(qd.views.talk.GatesView);
            },
            'talk/calls': function () {
                initView(qd.views.talk.CallsView);
            },
            'talk/locks': function () {
                initView(qd.views.talk.LocksView);
            },
            'maintain/card': function () {
                initView(qd.views.maintain.CardView);
            } ,
            'system/upgrade': function () {
                initView(qd.views.upgrade.MainView);
            },
            'agw/upgrade': function () {
                initView(qd.views.upgrade.AgwUpgradeView);
            },
            'dashborad/analysis': function () {
                initView(qd.views.dashborad.DashboradView);
            },
            'setting/modify_passwd': function () {
                initView(qd.views.setting.ModifyPasswdView);
            },
            '':function () {
                initView(qd.views.dashborad.DashboradView);
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
