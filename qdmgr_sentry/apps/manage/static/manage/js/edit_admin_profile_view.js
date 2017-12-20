
var edit_admin_profile_view = Backbone.View.extend({
    className: 'edit-admin-profile-view',
    template: versionify(CONST.static_url+'manage/ejs/edit_admin_profile_block.html'),

    initialize: function() {
        $(this.el).html(new EJS({url: this.template}).render({})); 
    }
});
