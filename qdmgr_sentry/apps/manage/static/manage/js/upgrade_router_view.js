
var upgrade_router_view = Backbone.View.extend({
    className: 'upgrade-router-view',
    template: versionify(CONST.static_url+'manage/ejs/home_upgrade_router_block.html'),
    device_type: 'router',
    build: 0,
    floor: 0,

    initialize: function() {
        this.$el.html(new EJS({url: this.template}).render({})); 
        this.get_upgrade_config(this.device_type);
    },

    events: {
        'click .view-build-statistics': function() {
            this.build = 0; this.floor = 0;
            this.get_router_stats(this.build,this.floor);
        },
        'click .view-floor-statistics': function() {
            this.build = parseInt($(event.srcElement || event.target).parents('a.view-floor-statistics').data('build'));
            this.floor = 0;
            this.get_router_stats(this.build,this.floor);
        },
        'click .view-room-statistics': function() {
            this.build = parseInt($(event.srcElement || event.target).parents('a.view-room-statistics').data('build'));
            this.floor = parseInt($(event.srcElement || event.target).parents('a.view-room-statistics').data('floor'));
            this.get_router_stats(this.build,this.floor);
        },
        'click .execute-upgrade-router-btn': function() {
            if (!$('input[name="upgrade_router_package"]').val().trim() || 
                !$('input[name="upgrade_router_version"]').val().trim()) {
                $('.notifications').notify({
                    type: 'danger', fadeOut: { enabled: true, delay: 3000 }, 
                    message: { text: '请填写完整信息' } 
                }).show();
                return false;
            }

            var view = this;
            $.ajax({
                url: '/ajax/upgrade/submit_upgrade_config',
                type: 'post',
                dataType: 'json',
                data: {
                    device_type: this.device_type,
                    file_uri: $('input[name="upgrade_router_package"]').val(),
                    version : $('input[name="upgrade_router_version"]').val()
                },
                success: function(result) {
                    if (result['err'] != 0) {
                        $('.notifications').notify({
                            type: 'danger', fadeOut: { enabled: true, delay: 3000 }, 
                            message: { text: result.msg } 
                        }).show();
                        return false;
                    }

                    view.build = 0; view.floor = 0;
                    view.get_upgrade_config(view.device_type);

                    $('.upgrade-router-package-display').html($('.upgrade-router-package-editor input').val());
                    $('.upgrade-router-package-editor').addClass('hide');
                    $('.upgrade-router-package-display').removeClass('hide');

                    $('.upgrade-router-version-display').html($('.upgrade-router-version-editor input').val());
                    $('.upgrade-router-version-editor').addClass('hide');
                    $('.upgrade-router-version-display').removeClass('hide');

                    $('.terminated-upgrade-router-state').addClass('hide');
                    $('.executing-upgrade-router-state').removeClass('hide');
                    $('.execute-upgrade-router-btn').addClass('hide');
                    $('.terminate-upgrade-router-btn').removeClass('hide');
                }
            });
        },
        'click .terminate-upgrade-router-btn': function() {
            $('.upgrade-router-package-editor').removeClass('hide');
            $('.upgrade-router-package-display').addClass('hide');

            $('.upgrade-router-version-editor').removeClass('hide');
            $('.upgrade-router-version-display').addClass('hide');

            $('.terminated-upgrade-router-state').removeClass('hide');
            $('.executing-upgrade-router-state').addClass('hide');
            $('.execute-upgrade-router-btn').removeClass('hide');
            $('.terminate-upgrade-router-btn').addClass('hide');

            $.ajax({
                url: '/ajax/upgrade/terminate_upgrade_process',
                type: 'post',
                dataType: 'json',
                data: {
                    device_type: this.device_type,
                },
                success: function(result) {
                    !!timer.config_timer && clearTimeout(timer.config_timer);
                    timer.config_timer = null;
                }
            });
        }
    },

    get_router_stats: function(build,floor) {
        $.ajax({
            url: '/ajax/upgrade/get_upgrade_stats',
            type: 'post',
            dataType: 'json',
            data: {
                device_type: 'router',
                build: build,
                floor: floor
            },
            success: function(result) {
                if (build==0 && floor==0) {
                    var ejs_html = new EJS({url: CONST.static_url+'manage/ejs/home_upgrade_router_statistics_for_build.html'})
                                    .render({build_stats: result.data.build_stats});
                    $('.upgrade-statistics-block').html(ejs_html);
                } else if (build != 0 && floor==0) {
                    var ejs_html = new EJS({url: CONST.static_url+'manage/ejs/home_upgrade_router_statistics_for_floor.html'})
                                    .render({build: build, floor_stats: result.data.floor_stats});
                    $('.upgrade-statistics-block').html(ejs_html);
                } else {
                    var ejs_html = new EJS({url: CONST.static_url+'manage/ejs/home_upgrade_router_statistics_for_room.html'})
                                    .render({build: build, floor: floor, room_stats: result.data.room_stats});
                    $('.upgrade-statistics-block').html(ejs_html);
                }
            }
        });
    },

    get_upgrade_config: function(device_type) {
        var view = this;

        $.ajax({
            url: '/ajax/upgrade/get_upgrade_config',
            type: 'post',
            dataType: 'json',
            data: {
                device_type: device_type
            },
            success: function(result) {
                var upgrade_config = result['data']['upgrade_config'];
                $('input[name="upgrade_router_package"]').val(upgrade_config['file_uri']);
                $('input[name="upgrade_router_version"]').val(upgrade_config['version']);

                if (upgrade_config['status'] == '1') {
                    $('.upgrade-router-package-editor').removeClass('hide');
                    $('.upgrade-router-package-display').addClass('hide');

                    $('.upgrade-router-version-editor').removeClass('hide');
                    $('.upgrade-router-version-display').addClass('hide');

                    $('.terminated-upgrade-router-state').removeClass('hide');
                    $('.executing-upgrade-router-state').addClass('hide');
                    $('.execute-upgrade-router-btn').removeClass('hide');
                    $('.terminate-upgrade-router-btn').addClass('hide');
                    
                    !!timer.config_timer && clearTimeout(timer.config_timer);
                    timer.config_timer = null;

                } else {
                    $('.upgrade-router-package-display').html($('.upgrade-router-package-editor input').val());
                    $('.upgrade-router-package-editor').addClass('hide');
                    $('.upgrade-router-package-display').removeClass('hide');

                    $('.upgrade-router-version-display').html($('.upgrade-router-version-editor input').val());
                    $('.upgrade-router-version-editor').addClass('hide');
                    $('.upgrade-router-version-display').removeClass('hide');

                    $('.terminated-upgrade-router-state').addClass('hide');
                    $('.executing-upgrade-router-state').removeClass('hide');
                    $('.execute-upgrade-router-btn').addClass('hide');
                    $('.terminate-upgrade-router-btn').removeClass('hide');

                    view.get_router_stats(view.build,view.floor);

                    timer.config_timer = setTimeout(function() { 
                        view.get_upgrade_config(device_type); 
                    }, 10000);
                }
            }
        });
    }
});

