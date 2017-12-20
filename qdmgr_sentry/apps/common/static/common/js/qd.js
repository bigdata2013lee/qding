(function ($) {
    var consoleEnable = true; //是否启用控制台,在布置时设置为false
    if (!consoleEnable) {
        if (!window.console) {
            window.console = {};
        }
        console.info = function () {
        };
        console.log = function () {
        };
        console.debug = function () {
        };
        console.warn = function () {
        };
        console.error = function () {
        };
    }


    //----------------命名空间初始化--------------------------
    window.qd = {};

    qd.ns = qd.nameSpace = function (ns) {
        var a = arguments, o = qd;
        var x = ns.split('.');
        for (var i = 0; i < x.length; i++) {
            o[x[i]] ? "" : o[x[i]] = {};
            o = o[x[i]];
        }
        return o;

    };


    qd.importCss = function (url) {
        var head = $("head:first");
        if (head.find('link[href="' + url + '"]').size() == 0) {
            var link = $('<link rel="stylesheet" type="text/css" href="' + url + '"/>');
            $("head:first").append(link);
        }
    };


    qd.brake_rpc = function (url, params, disable_msg_fun) {
        if (!params) {
            params = {};
        }
        else if (typeof params == 'function') {
            var _params = params;
            params = _params();
        }
        var _type = 'POST';
        if (/\.json\s*$/i.test(url)) {
            _type = 'GET';
        }
        var _ajax = $.ajax({
                type: _type, dataType: 'json', url: url, data: params
            })
            .success(function (result) {

            })
            .error(function () {

            });

        return _ajax;
    };

    /**
     * 创建、原型继承类
     * @param supper: 父类, 可选参数
     * @param props: 属性及方法
     * var Person  = qd.Class(super, {
     *     __init__: function(name){ this.name = name;}
     *     sayHello: function(){console.info("Hello everyone. I am %s", this.name)}
     * })
     */
    qd.Class = function () {
        if (arguments.length == 0) {
            throw new Error("Argument error! Create new class, please writting as: Class([super], {...})");
        }
        var superCls = arguments.length == 2 ? arguments[0] : function () {
        };
        var newCls = function () {
            this.__super__ = superCls;
            if (this.__init__) this.__init__.apply(this, arguments);
        };
        var pros = arguments.length == 1 ? arguments[0] : arguments[1];

        for (var key in superCls.prototype) {
            newCls.prototype[key] = superCls.prototype[key];
        }

        for (var key in pros) {
            newCls.prototype[key] = pros[key];
        }

        return newCls;
    };

    //-------------------------------------------------------------------------------//
    var utils = qd.utils = {};


    /**
     * 格式化字符串
     * 示例代码:
     * formatStr('Hello {0}, I klie {1}','word', 'JS');
     * >>>Hello word, I klie JS
     */
    utils.formatStr = function () {
        var str = arguments[0];
        for (var i = 1; i < arguments.length; i++) {
            var reg = eval("(/\\{\\s*" + (i - 1) + "\\s*\\}/gi)");
            str = str.replace(reg, arguments[i]);
        }
        return str;
    };


    utils.getTimeStr = function (time, sortFormat) {
        var fm = "{0}-{1}-{2} {3}:{4}";
        if (sortFormat) {
            fm = "{0}-{1}-{2}";
        }
        var fix0 = function (n) {
            if (n < 10) return "0" + n;
            return n + "";
        };
        if (time == 0) return "";
        if (time * 1 == NaN) return '';
        var d = new Date();
        d.setTime(time * 1);
        return utils.formatStr(fm, d.getFullYear(),
            fix0(d.getMonth() + 1), fix0(d.getDate()), fix0(d.getHours()), fix0(d.getMinutes()))
    };


    utils.val2boolean = function (val) {
        if (val == "是" || val == "yes" || val == "true") return true;
        if (val == "否" || val == "no" || val == "false") return false;

        if (val) return true;
        return false;
    }

    utils.val2booleanStr = function (val) {
        if (val == "是" || val == "yes" || val == "true") return true + "";
        if (val == "否" || val == "no" || val == "false") return false + "";
        if (val) return true + "";
        return false + "";
    }

    /**
     * 删除对象属性
     * simple: delattrs(obj, "name", "age", ...)
     */
    utils.delattrs = function () {
        if (arguments.length < 2) return;
        var obj = arguments[0]
        if (!obj) return;

        for (var i = 1, len = arguments.length; i < len; i++) {
            delete obj[arguments[i]];
        }
    }

    utils.Observer = function () {
        this.events = {};

        /** 触发事件  */
        this.fireEvent = function (eName) {
            var events = this.events[eName];
            if (!events) return;

            var handlerArguments = [];
            for (var i = 1; i < arguments.length; i++) {
                handlerArguments.push(arguments[i]);
            }

            for (var i = 0; i < events.length; i++) {
                var event = events[i];
                event.handler.apply(event.scope || this, handlerArguments);
            }

        };

        /** 事件绑定 */
        this.on = function (eName, handler, scope) {
            if (!this.events[eName])  this.events[eName] = [];
            this.events[eName].push({handler: handler, scope: scope});
        };

        /** 取消事件，如果handler不存在，取消所有事件 */
        this.un = function (eName, handler) {
            var events = this.events[eName];
            if (!events || events.length == 0) return;
            if (events && !handler) {
                events.splice(0, events.length);
                return;
            }


            for (var i = events.length - 1; i >= 0; i--) {
                if (events[i].handler == handler) events.splice(i, 1);
            }
        }
    };


    //延时任务管理功能
    utils.DelayTaskMrg = {
        _tasks: {},
        _DelayTask: function (xfun) {
            //console.info('new _DelayTask...');
            this.time = 800;
            /** 执行 */
            this.excute = function () {
                xfun(arguments);
            };

            /**
             * 运行, 在time毫秒内再次执行此任务，上次未执行任务将被取消
             * @note 处理函数参数在time参数后面加入
             * @param {int} time
             */
            this.run = function (time) {
                if (time) {
                    this.time = time;
                }
                clearTimeout(this._taskTimer);
                var newArguments = [];
                for (var i = 1; i < arguments.length; i++) {
                    newArguments.push(arguments[i]);
                }
                this._taskTimer = setTimeout(function () {
                    xfun.apply({}, newArguments)
                }, this.time);
            }

        },
        /**
         * 创建延时任务
         * @param {String} id 唯一任务ID，如果id已经存在，则返回已创建的任务对象
         * ＠param {Function} xfun 任务处理函数
         */
        createTask: function (id, xfun) {
            if (this._tasks[id]) return this._tasks[id];
            var task = new this._DelayTask(xfun);
            this._tasks[id] = task;
            return task;
        }
    };

    utils.delayTask = function (tid, xfun, time) {
        utils.DelayTaskMrg.createTask(tid, xfun).run(time);
    }


    //-------------------------------------校验方法-----------------------------------------------------//

    utils.isEmpty = function (obj) {
        if ($.type(obj) == 'string' && obj == '') {
            return true
        }
        return $.isEmptyObject(obj);

    }
    utils.isValidIp = function (ip) {
        if (ip == "255.255.255.255")return false;
        if (/^0{1,3}\.0{1,3}\.0{1,3}\.0{1,3}$/.test(ip)) return false;

        var exp = /^(?:(?:[1-9]?[0-9]|1[0-9]{2}|2(?:[0-4][0-9]|5[0-5]))\.){3}(?:[1-9]?[0-9]|1[0-9]{2}|2(?:[0-4][0-9]|5[0-5]))$/;
        if (exp.test(ip)) {
            return true
        }
        return false


    };

    utils.isValidUrl = function (ip) {
        var exp = /^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?$/;
        if (exp.test(ip)) {
            return true
        }
        return false
    };

    utils.isValidMac = function (ip) {
        var exp = /^\s*([0-9a-fA-F]{2,2}[:|-]){5,5}[0-9a-fA-F]{2,2}\s*$/;
        if (exp.test(ip)) {
            return true
        }
        return false
    };


    utils.isVaildEmail = function (email) {
        var exp = /^[0-9a-zA-Z_\.#]+@(([0-9a-zA-Z]+)[.])+[a-z]{2,4}$/;
        if (exp.test(email)) {
            return true
        }
        return false
    };

    utils.isVaildPhone = function (phone) {
        var exp1 = /^0\d{2,3}-\d{7,8}$/;
        var exp2 = /^1\d{10,10}$/;

        if (exp1.test(phone) || exp2.test(phone)) {
            return true;
        }
        return false;
    }


    utils.isValidNum = function (val) {
        var exp = /^-?\d+(\.\d+)?$/;
        if (exp.test(val)) {
            return true
        }
        return false
    }

    utils.memberInList = function(mem, list) {
        for(var i=0;i<list.length;i++){
            if(list[i] == mem){
                return true;
            }
        }
        return false;
    }

    utils.valueInDictList = function(value, k, dictList) {
        for(var i=0; i<dictList.length;i++){
            if(dictList[i][k] == value){
                return true;
            }
        }
        return false;
    }

    //--------------------------------------------------------------------------------------//


    /**
     * trim 对象属性的空格，只对字符类型的属性有效
     * @param {Object} obj
     * @param {Object} pns 可选参数，属性名列表
     */
    utils.trimObj = function (obj, pns) {
        $.each(obj, function (key, value) {
            if (typeof value !== 'string') return;
            if (!pns || pns.length == 0) {
                obj[key] = $.trim(value);
            }
            else if ($.inArray(key, pns) >= 0) {
                obj[key] = $.trim(value);
            }
        });
    };

    utils.fillSelect = function (el, data, options) {
        var _options = {default_value: "", default_label: '-- 选择 --'};
        $.extend(_options, options);
        $(el).html('');
        $(el).append(utils.formatStr('<option value="{0}">{1}</option>', _options.default_value, _options.default_label));
        $.each(data, function (i, item) {
            var option_value = eval('item' + _options['value']);
            var option_label = eval('item' + _options['label']);
            $(el).append(utils.formatStr('<option value="{0}">{1}</option>', option_value, option_label));
        });

    };

    utils.serialize = function (el) {
        var serialize_obj = {};
        $(el).find(':hidden, :text,:password,textarea,select, :checkbox:checked, :radio:checked').each(function () {
            var name = $.trim($(this).attr('name') || "");
            var value = $.trim($(this).val() || "");
            if (name == '') {
                return;
            }
            serialize_obj[name] = value;
        });

        return serialize_obj;
    }


    qd.notify = {
        success: function (msg) {
            $('.notifications').notify({type: 'success', message: msg}).show();
        },
        info: function (msg) {
            $('.notifications').notify({type: 'info', message: msg}).show();
        },
        error: function (msg) {
            $('.notifications').notify({type: 'danger', message: msg}).show();
        }
    };

    qd.mk_pagination = function (pagination) {
        if (!pagination) return '';
        var template = $('script[name=pagination_template]').html();

        var compiled = _.template(template);
        return compiled({pagination: pagination});

    }

    qd.render_template=function(tmp_name, data, container){

        var template = $('script[name='+tmp_name+'_template]').html();
        var compiled = _.template(template);
        var html =  compiled(data);
        if(container){
            $(container).html('').html(html);
        }
        return  html;

    };


    $.fn.extend({
        /**
         * 把数据渲染到指定的模板中
         * @param data
         * @param tmp_name, 可选参数, 可以在container el 的data中指定
         */
        render_template:function (data, tmp_name) {
            if(! tmp_name || tmp_name == ""){tmp_name = this.data('template');}
            if(! tmp_name || tmp_name == ""){throw new Error("Template name is not valid.")}
            qd.render_template(tmp_name, data, this);
        }
    });


    qd.load_view_tpls = function (url) {
        $.ajax({
            url: url,async: false,
            success: function (html) {
                $("#view_templates").html(html);
            }

        });
    };


    qd.render_empty_tr = function (data_list) {
        if (data_list && data_list.length > 0) {
            return '';
        }
        var html = '<tr><td colspan="30"><center style="color:#ccc">暂无数据...</center></td></tr>';
        return html;
    }


})(jQuery);
