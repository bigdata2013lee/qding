(function ($) {

    /**
     * //读卡-写卡
     * _qd_card_reader.invoke("read_card")
     * _qd_card_reader.invoke("write_card", {str_data:"123456781234567812345678123456781234567812345678123456781234567812345678123456781234567812345678"})
     *
     */
    var card_reader = window._qd_card_reader = {

        _init_ws: function () {
            var wsUri = "ws://127.0.0.1:8777/";
            var ws = this.ws = new WebSocket(wsUri);

            ws.onmessage = function (evt) {
                var data = JSON.parse(evt.data);
                if ("invoke" in data) {
                    $(document).trigger("invoke/" + data.invoke, data.result);
                }

            };
            
            ws.onopen = function (evt) { /**console.info(evt);*/ };
            ws.onclose = function (evt) { /**console.info(evt);*/ };
            ws.onerror = function (evt) { /**console.info(evt);*/ };
        },
        
        invoke: function (method, params) {
            if (!params) { params = {} }
            this.ws.send(JSON.stringify({method: method, params: params}));
        }
    };





    $(document).ready(function (evt) {
        card_reader._init_ws();
        
        $(document).bind("invoke/read_card", function (evt, result) {
            console.info(result);
            $("span.accept_card_reader_info").html(result);
        });

        $(document).bind("invoke/write_card", function (evt, result) {
            console.info(result);
            $("span.accept_card_reader_info").html(result);
        });



        /*--------------------- exec invoke --------------------*/
        $("button.read_card").bind("click", function (evt) {
            _qd_card_reader.invoke("read_card");
        });

        $("button.write_card").bind("click", function (evt) {
            _qd_card_reader.invoke("write_card", {str_data:"123456781234567812345678123456781234567812345678123456781234567812345678123456781234567812345678"});
        });


    });



})(jQuery);