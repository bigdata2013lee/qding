

if(!Number.prototype.shorten_number) {
    Number.prototype.shorten_number = function(float_count) { 
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
        if(number >= 10000) {
            number /= 10000;
            counter += 4;
        }
        if (typeof(float_count) != 'undefined') {
            return str + (counter == 4 ? "万" : (counter == 8 ? "亿" : ""));
        }
        while(str.charAt(str.length - 1) == '0')
            str = str.substring(0, str.length - 1);
        if(str.charAt(str.length - 1) == '.')
            str = str.substring(0, str.length - 1);
        return str + (counter == 4 ? "万" : (counter == 8 ? "亿" : ""));
    }
}


if(!String.prototype.trim) {
    String.prototype.trim = function() { return this.replace(/(^\s*)|(\s*$)/g,''); }
}


if(!String.prototype.truncate) {
    String.prototype.truncate = function(len,end) { 
        var truncate_str = '';
        var charlens = 0;
        for(var　i=0;i<this.length;i++) {
            var charcode = this.charCodeAt(i);
            if　(charcode>=33 && charcode<=126) {
                charlens = charlens + 1;
            } else {
                charlens = charlens + 2;
            }

            if (charlens>len*2) {
                break;
            } else {
                truncate_str = truncate_str + this.substr(i,1);
            }
        }

        end = end==null ? '...':end;
        return truncate_str+(truncate_str==this ? '':end); 
    };
}


if(!Date.prototype.parseISO8601) {
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

            if (d[3]) { date.setMonth(Number(d[3]) - 1); }
            if (d[5]) { date.setDate(Number(d[5])); }
            if (d[8]) { date.setHours(Number(d[8])); }
            if (d[9]) { date.setMinutes(Number(d[9])); }
            if (d[11]) { date.setSeconds(Number(d[11])); }
            if (d[15]) {
                offset = (Number(d[15]) * 60) + Number(d[16]);
                offset *= ((d[14] == '-') ? -1 : 1);
            }

            offset += date.getTimezoneOffset();
            time = (Number(date) + (offset * 60 * 1000));
            this.setTime(Number(time));
        }

        return this;
    }
}


if(!Date.prototype.format) {
    Date.prototype.format = function(format) { 
        var o = { 
            'M+': this.getMonth()+1,                    //month 
            'd+': this.getDate(),                       //day 
            'h+': this.getHours(),                      //hour 
            'm+': this.getMinutes(),                    //minute 
            's+': this.getSeconds(),                    //second 
            'q+': Math.floor((this.getMonth()+3)/3),    //quarter 
            'S': this.getMilliseconds()                 //millisecond 
        } 

        if (/(y+)/.test(format)) {
            format = format.replace(RegExp.$1,(this.getFullYear()+'').substr(4 - RegExp.$1.length)); 
        }

        for (var k in o) {
            if(new RegExp('('+ k +')').test(format)) {
                format = format.replace(RegExp.$1,RegExp.$1.length==1 ? o[k] : ('00'+ o[k]).substr((''+ o[k]).length)); 
            }
        }

        return format; 
    }
}


if(!Date.prototype.humanize) {
    Date.prototype.humanize = function(default_format,flag) { 
        var gap = (Date.parse(new Date())-Date.parse(this))/1000;

        if (gap < 60) {
            return '刚刚';
        } else if (gap < 3600) {
            return parseInt(gap/60) + '分钟前';
        } else if (gap < 86400) {
            return parseInt(gap/3600) + '小时前';
        } else if (gap < 86400 * 2) {
            return '昨天';
        } else if (gap < 86400 * 3) {
            return '前天';
        } else if (flag) {
            return this.format(default_format || 'yyyy-MM-dd'); 
        } else if (gap < 86400 * 30) {
            return parseInt(gap/86400) + '天前';
        } else if (gap < 86400 * 30 * 6) {
            return parseInt(gap/86400/30) + '个月前';
        }

        return this.format(default_format || 'yyyy-MM-dd'); 
    }
}



//////////////////////////////////////////////////////////////////////////////////////////


var const_id_type_list = {
    '1': '身份证',
    '2': '护照',
    '3': '军官证',
    '4': '港澳台通行证',
    '5': '会员证',
    '6': '其它证件'
};


var const_weekday_list = {
    0: '星期日',
    1: '星期一',
    2: '星期二',
    3: '星期三',
    4: '星期四',
    5: '星期五',
    6: '星期六'
};


var global = {
    xhr: null,      // XMLHttpRequest
    result: null
};



//////////////////////////////////////////////////////////////////////////////////////////




function render_css(selector,options) {
    selector.removeAttr('style');

    for (var item in options) {
        selector.css(item,options[item]);
    }

    if(selector.children().length != 0)
        render_css(selector.children(),options);
}



function isWinPC(user_agent) {
    var agents = new Array('android', 'iphone', 'symbianos', 'windows phone', 'ipad', 'ipod');  
    var flag = true;  
    for (var i=0;i<agents.length;i++) {  
        if (user_agent.toLowerCase().indexOf(agents[i])>0) { 
            flag = false; 
            break; 
        }  
    }  
    return flag;
}



function bind_geo_selector(province,city) {
    $.ajax({
        url: '/ajax/common/geo/province/list?_t='+new Date().getTime(),
        type: 'POST',
        data: { },
        dataType: 'json',
        success: function(result) {
            global.result = result;
            if (result.err != 0) {
                $('.notifications').notify({type: 'danger', message: result.msg}).show();
                $('.login-btn').button('reset');
                console.log(result);
                return false;
            }

            $(province.selector).html('<option value="">'+province.label+'</option>');
            var province_list = result.data.collection;
            for (var i=0;i<province_list.length;i++) {
                var option = $('<option></option>');
                option.prop('value',province_list[i].id);
                option.html(province_list[i].name);
                $(province.selector).append(option);
            }

            $(province.selector).unbind('change');
            $(province.selector).bind('change',function() {
                $.ajax({
                    url: '/ajax/common/geo/city/list?_t='+new Date().getTime(),
                    type: 'POST',
                    data: { 
                        province_id: $(province.selector).val()
                    },
                    dataType: 'json',
                    success: function(result) {
                        global.result = result;
                        if (result.err != 0) {
                            $('.notifications').notify({type: 'danger', message: result.msg}).show();
                            console.log(result);
                            return false;
                        }

                        $(city.selector).html('<option value="">'+city.label+'</option>');
                        var city_list = result.data.collection;
                        for (var i=0;i<city_list.length;i++) {
                            var option = $('<option></option>');
                            option.prop('value',city_list[i].id);
                            option.html(city_list[i].name);
                            $(city.selector).append(option);
                        }

                        if (!!city.value) {
                            $(city.selector).val(city.value);
                            city.value = null;
                        }

                        if (city_list.length==1) {
                            $(city.selector).val(city_list[0].id);
                        }
                    }
                });
            });

            if (!!province.value) {
                $(province.selector).val(province.value);
            }

            $(province.selector).change();
        }
    });
}




function make_ajax(args) {
    if (!!args.form) {
        args.form.ajaxSubmit({
            url: args.url,
            type: 'POST',
            dataType: 'json',
            beforeSubmit: function(form_data, jq_form, options) {
                if (!!args.data) {
                    for (var key in args.data) {
                        form_data.push({ name: key, value: args.data[key] });
                    }
                }
            },
            success: function(result, text_status, xhr) {
                global.xhr = xhr;
                global.result = result;

                if (result.err != 0) {
                    if (!!args.fail) {
                        args.fail(result);
                    } else {
                        $('.notifications').notify({type: 'danger', message: result.msg}).show();
                        !!args.complete && args.complete(xhr,text_status);
                    }

                } else {
                    !!args.success && args.success(result);
                }
            },
            error: function(xhr,text_status,error_thrown) {
                !!args.error && args.error(xhr,text_status,error_thrown);
            },
            complete: function(xhr,text_status) {
                global.xhr = xhr;
                /**
                if (xhr.status != 200) {
                    var msg = xhr.state()+' - '+xhr.status+' - '+xhr.statusText;
                    $('.notifications').notify({type: 'danger', message: msg}).show();
                }
                **/

                !!args.complete && args.complete(xhr,text_status);
            }
        });

    } else {
        $.ajax({
            url: args.url,
            data: args.data || {},
            type: 'POST',
            dataType: 'json',
            success: function(result,text_status) {
                global.result = result;

                if (result.err != 0) {
                    if (!!args.fail) {
                        args.fail(result);
                    } else {
                        $('.notifications').notify({type: 'danger', message: result.msg}).show();
                    }

                } else {
                    !!args.success && args.success(result);
                }
            },
            error: function(xhr,text_status,error_thrown) {
                !!args.error && args.error(xhr,text_status,error_thrown);
            },
            complete: function(xhr,text_status) {
                global.xhr = xhr;
                /**
                if (xhr.status != 200) {
                    var msg = xhr.state()+' - '+xhr.status+' - '+xhr.statusText;
                    $('.notifications').notify({type: 'danger', message: msg}).show();
                }
                **/

                !!args.complete && args.complete(xhr,text_status);
            }
        });
    }
};




