function compute_pagination(pagination, num_len) {
    var page_count = Math.ceil(pagination.total_count / pagination.page_size);
    page_count = (page_count === 0) ? 1 : page_count;
    pagination.page_no = Number(pagination.page_no);
    pagination.page_no = (pagination.page_no < page_count) ? pagination.page_no : page_count;
    var start_no = pagination.page_no;
    var end_no = pagination.page_no;

    for (var i = (num_len || 5); i > 1;) {
        if (start_no > 1 && i > 0) {
            start_no--;
            i--;
            if (i === 0) break;
        }
        if (end_no < page_count && i > 0) {
            end_no++;
            i--;
            if (i === 0) break;
        }
        if (start_no == 1 && end_no == page_count) break;
    }
    pagination.page_count = page_count;
    pagination.start_no = start_no;
    pagination.end_no = end_no;
    return pagination;
}

// 工具类库
var Util = {
    const_id_type_list: {
        '1': '身份证',
        '2': '护照',
        '3': '军官证',
        '4': '港澳台通行证',
        '5': '会员证',
        '6': '其它证件'
    },

    const_weekday_list: {
        0: '星期日',
        1: '星期一',
        2: '星期二',
        3: '星期三',
        4: '星期四',
        5: '星期五',
        6: '星期六'
    },

    init: function () {
        if (!Number.prototype.shorten_number) {
            Number.prototype.shorten_number = function (float_count) {
                var counter = 0;
                var number = this;
                if (number >= 100000000) {
                    number /= 100000000;
                    counter = 8;
                } else if (number >= 10000) {
                    number /= 10000;
                    counter = 4;
                }
                var fix = (typeof(float_count) != 'undefined' ? float_count : 2);
                var str = number.toFixed(fix);
                if (number >= 10000) {
                    number /= 10000;
                    counter += 4;
                }
                if (typeof(float_count) != 'undefined') {
                    return str + (counter == 4 ? "万" : (counter == 8 ? "亿" : ""));
                }
                while (str.charAt(str.length - 1) == '0')
                    str = str.substring(0, str.length - 1);
                if (str.charAt(str.length - 1) == '.')
                    str = str.substring(0, str.length - 1);
                return str + (counter == 4 ? "万" : (counter == 8 ? "亿" : ""));
            };
        }

        if (!String.prototype.trim) {
            String.prototype.trim = function () {
                return this.replace(/(^\s*)|(\s*$)/g, '');
            };
        }

        if (!String.prototype.truncate) {
            String.prototype.truncate = function (len, end) {
                var truncate_str = '';
                var charlens = 0;
                for (var i = 0; i < this.length; i++) {
                    var charcode = this.charCodeAt(i);
                    if (charcode >= 33 && charcode <= 126) {
                        charlens = charlens + 1;
                    } else {
                        charlens = charlens + 2;
                    }

                    if (charlens > len * 2) {
                        break;
                    } else {
                        truncate_str = truncate_str + this.substr(i, 1);
                    }
                }

                end = end == null ? '...' : end;
                return truncate_str + (truncate_str == this ? '' : end);
            };
        }

        if (!Date.prototype.parseISO8601) {
            Date.prototype.parseISO8601 = function (string) {
                if (!string) {
                    this.setTime(new Date());
                } else {
                    var regexp = "([0-9]{4})(-([0-9]{2})(-([0-9]{2})" +
                        "((T|\\s)([0-9]{2}):([0-9]{2})(:([0-9]{2}))?" +
                        "(Z|(([-+])([0-9]{2}):([0-9]{2})))?)?)?)?";
                    var d = string.match(new RegExp(regexp));

                    var offset = 480; // +08:00
                    var date = new Date(Number(d[1]), 0, 1);

                    if (d[3]) {
                        date.setMonth(Number(d[3]) - 1);
                    }
                    if (d[5]) {
                        date.setDate(Number(d[5]));
                    }
                    if (d[8]) {
                        date.setHours(Number(d[8]));
                    }
                    if (d[9]) {
                        date.setMinutes(Number(d[9]));
                    }
                    if (d[11]) {
                        date.setSeconds(Number(d[11]));
                    }
                    if (d[15]) {
                        offset = (Number(d[15]) * 60) + Number(d[16]);
                        offset *= ((d[14] == '-') ? -1 : 1);
                    }

                    offset += date.getTimezoneOffset();
                    time = (Number(date) + (offset * 60 * 1000));
                    this.setTime(Number(time));
                }
                return this;
            };
        }

        if (!Date.prototype.format) {
            Date.prototype.format = function (format) {
                var o = {
                    'M+': this.getMonth() + 1,                    //month
                    'd+': this.getDate(),                       //day 
                    'h+': this.getHours(),                      //hour 
                    'm+': this.getMinutes(),                    //minute 
                    's+': this.getSeconds(),                    //second 
                    'q+': Math.floor((this.getMonth() + 3) / 3),    //quarter
                    'S': this.getMilliseconds()                 //millisecond 
                }

                if (/(y+)/.test(format)) {
                    format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
                }

                for (var k in o) {
                    if (new RegExp('(' + k + ')').test(format)) {
                        format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ('00' + o[k]).substr(('' + o[k]).length));
                    }
                }

                return format;
            };
        }

        if (!Date.prototype.humanize) {
            Date.prototype.humanize = function (default_format, flag) {
                var gap = (Date.parse(new Date()) - Date.parse(this)) / 1000;

                if (gap < 60) {
                    return '刚刚';
                } else if (gap < 3600) {
                    return parseInt(gap / 60) + '分钟前';
                } else if (gap < 86400) {
                    return parseInt(gap / 3600) + '小时前';
                } else if (gap < 86400 * 2) {
                    return '昨天';
                } else if (gap < 86400 * 3) {
                    return '前天';
                } else if (flag) {
                    return this.format(default_format || 'yyyy-MM-dd');
                } else if (gap < 86400 * 30) {
                    return parseInt(gap / 86400) + '天前';
                } else if (gap < 86400 * 30 * 6) {
                    return parseInt(gap / 86400 / 30) + '个月前';
                }

                return this.format(default_format || 'yyyy-MM-dd');
            };
        }
    },

};
Util.init();

// UI类库
var UI = {
    /**
     * 创建loading
     * @param {String} id     loading创建在对应id的dom元素内容
     * @param {String} text   需要修改的文字
     * @param {String} state  判断是否成功/失败，显示对应样式
     */
    loading: function (text, id, state) {
        var str = '',
            text = text ? text : "正在加载...",
            iconCls = 'fa-spinner fa-spin',
            obj = "body",
            loadCls = "loading";
        // 判断是否已经有loading
        var isload = document.getElementById("loading");
        if (isload) {
            return;
        }
        if (id) {
            obj = "#" + id;
            height = $(obj).height();
            loadCls = "loading-abs";
        } else {
            height = $(window).height();
        }
        if (state) {
            iconCls = state === "success" ? "fa-check-circle" : "fa-times-circle";
        }
        str += '<div id="loading" class="' + loadCls + '"><div class="loading-con"><i class="fa ' + iconCls + '"></i>';
        str += '<p>' + text + '</p>';
        str += '</div></div>';
        $(obj).append(str);
        $("#loading").css("top", height / 2 - 62);
        if (state) {
            var _this = this;
            setTimeout(function () {
                _this.removeLoading();
            }, 3500);
        }
    },
    // 删除loading
    removeLoading: function () {
        $("#loading").remove();
    },
    // 操作成功提示
    showSucTip: function (msg) {
        msg = msg || "操作成功";
        this.removeLoading();
        this.loading(msg, null, "success");
    },
    // 操作失败提示
    showErrTip: function (msg) {
        this.removeLoading();
        this.loading(msg, null, "error");
    },

    // 错误提示
    showTips: function (type, msg) {
        $('.notifications').notify({
            type: type,
            fadeOut: {
                enabled: true,
                delay: 3000
            },
            message: {
                text: msg
            }
        }).show();
    },
    // 创建简单下拉框选项
    createSimpleOption: function (obj, list) {
        var str = '';
        for (var i = 0; i < list.length; i++) {
            str += '<option value="' + list[i] + '">' + list[i] + '</option>';
        }
        obj.append(str);
    },

    createOption: function (obj, list, value_key, label_key, selected_str) {
        var str = '';
        for (var i = 0; i < list.length; i++) {
            str += '<option value="' + list[i][value_key] + '">' + list[i][label_key] + '</option>';
        }
        obj.append(str);
        obj.val(selected_str);
    },

};




