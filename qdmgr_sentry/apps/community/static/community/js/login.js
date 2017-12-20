function login() {
    $('.login-btn').button('loading');

    $.ajax({
        url: '/web_login',
        type: 'POST',
        data: {
            username: $('.login input[name="username"]').val(),
            password: $.md5($('.login input[name="password"]').val())
        },
        
        dataType: 'json',
        success: function(result) {
            if (result.data.flag=='Y') {
            	$('.alert').addClass('hide');
                window.location.href = result.data.url ;
            } else {
            	$('.text-danger').text(result.msg);
                $('.alert').removeClass('hide');
                $('.login-btn').button('reset');
            }
        }
    });
}



