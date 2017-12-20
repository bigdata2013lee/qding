
var global_xhr = null;
var x = null;


function output_response_header(el) {
    if (!!global_xhr) {
        $(el+' .response-header').html(global_xhr.getAllResponseHeaders().replace(new RegExp('\n','g'),'<br>'));
    }
}


function submit_ajax_request() {
    $('#ajax .submit-ajax-btn').button('loading');

    $('#ajax .request-error').html('');
    $('#ajax .response-header').html('');
    $('#ajax .output-text').html('');

    var url = $('#ajax input[name="url"]').val().trim();

    var type = $('#ajax select[name="type"]').val();
    var dataType = $('#ajax select[name="dataType"]').val();
    var data = '';
    
    for (var i=0;i<$('#ajax textarea[name="data"]').val().length;i++) {
        if ($('#ajax textarea[name="data"]').val()[i].charCodeAt()<32) continue;
        data += $('#ajax textarea[name="data"]').val()[i];
    }
    data = data.trim();

    str = "$.ajax({ url:'"+url+"', type:'"+type+"', dataType:'"+dataType+"', data:"+data+", beforeSend: function(xhr) {console.log(xhr);}, success: function(result) { $('#ajax .output-text').html('"+dataType+"'=='html' ? result : $.toJSON(result)); console.log(result); }, complete: function(xhr,ts) { $('#ajax .request-error').html(xhr.state()+' - '+xhr.status+' - '+xhr.statusText); output_response_header('#ajax'); $('#ajax .submit-ajax-btn').button('reset'); } });";

    try {
        if (!!global_xhr) global_xhr.abort();
        eval('global_xhr='+str);
    } catch(e) {
        $('#ajax .request-error').html(e.message);
        $('#ajax .response-header').html("<span>$.ajax({</span><br><span style='margin-left:30px;'>url: '</span><span style='color:red;'>"+url+"</span><span>',</span><br><span style='margin-left:30px;'>type: '</span><span style='color:red;'>"+type+"</span><span>',</span><br><span style='margin-left:30px;'>dataType: '</span><span style='color:red;'>"+dataType+"</span><span>',</span><br><span style='margin-left:30px;'>data: </span><span style='color:red;'>"+data+"</span><span>,</span><br><span style='margin-left:30px;'>success: function(result) { ... },</span><br><span style='margin-left:30px;'>complete: function(xhr, ts) { ... }</span><br><span>});</span>");
        $('#ajax .submit-ajax-btn').button('reset');
    }
}


function submit_upload_image() {
    $('#image .request-error').html('');
    $('#image .response-header').html('');
    $('#image .output-text').html('');

    var file_input = $('#image input[type="file"]')[0];
    if (file_input.files.length>0 && file_input.files[0].size>5*1024*1024) {
        alert('Image out of size');
        return false;
    }

    $('#image .upload-image-btn').button('loading');

    $('#upload_image_form').ajaxSubmit({
        url: '/api/common/upload_single_image',
        type: 'POST',
        dataType: 'html',
        success: function(result) {
            $('#image .output-text').html(result);

            result = $.parseJSON(result);
            if (result.err==0) {
                $('#upload_image_form .fileinput').fileinput('clear');
            }
            console.log(result);
        },
        complete: function(xhr, ts) {
            $('#image .request-error').html(xhr.state()+' - '+xhr.status+' - '+xhr.statusText);
            $('#image .upload-image-btn').button('reset');

            global_xhr = xhr;
            output_response_header('#image');
        }
    });
}

