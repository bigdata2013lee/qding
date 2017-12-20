(function () {

    if(window.FileReader) {
    var fr = new FileReader();  
    // add your code here
    }
    else {
        alert("Not supported by your browser!");
    }
    
    
    
    
    

    $(document).ready(function (evt) {

        $("#take_picture").bind("click", function (evt) {
            $("#file_input1").click();
        });

        $("#file_input1").bind("change", function (evt) {
            var file = evt.target.files[0];
            var fr = new FileReader();
            fr.onloadend = function (e) {
                document.getElementById("show-picture").src = e.target.result;
                $("body").trigger("preview_img_change");
            };

            fr.readAsDataURL(file);


        });
        
        
        $("#maker_win .btn-save").bind("click", function (evt) {
            view.append_to_pic_libs();
        });

        $("body").bind("preview_img_change", function (evt) {
            view.feature_compare();
        });
        
        
        var view = {
            
            append_to_pic_libs:function () {
                
                var params = {};
                
                params.name = $("#maker_win input[name=name]").val();
                if(params.name == ""){
                    qd.notify.error("请填写名称");
                    return;
                }
                
                var img_src = $("img#show-picture").attr("src");
                if(! /data:image/.test(img_src)){
                    qd.notify.error("未上传图片");
                    return;
                }
    
                params.img_base64 = img_src;
    
                qd.rpc("face.FaceApi.append_image", params).success(function (result) {
                    $("#maker_win input[name=name]").val("");
                    $("#maker_win").modal("hide");
                })                
                
            },

            feature_compare:function () {

                var params = {};
                var img_src = $("img#show-picture").attr("src");
                if(! /data:image/.test(img_src)){
                    qd.notify.error("未上传图片");
                    return;
                }

                params.img_base64 = img_src;

                qd.rpc("face.FaceApi.feature_compare", params).success(function (result) {
                    if(result.data.targets && result.data.targets.length>0){
                        qd.notify.success(result.data.targets[0].name + " sc:" + result.data.targets[0].score, 6000);
                    }

                    if(result.data["speek_txt"] && result.data["speek_txt"] != ""){
                        console.info(result.data["speek_txt"]);
                        $("#audio_speek").attr("src", "/speek/?speek_txt=" + result.data["speek_txt"]);
                    }
                })

            }
            
            
        }




    })

})(jQuery);