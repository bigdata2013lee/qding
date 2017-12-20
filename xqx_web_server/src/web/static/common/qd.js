(function($) {
	var consoleEnable = true; //是否启用控制台,在布置时设置为false
	if(!consoleEnable) {
		if(!window.console) { window.console = {}; }
		console.info = function() {};
		console.log = function() {};
		console.debug = function() {};
		console.warn = function() {};
		console.error = function() {};
	}

	//----------------命名空间初始化--------------------------
	window.qd = {};

	qd.ns = qd.nameSpace = function(ns) {
		var a = arguments,
			o = qd;
		var x = ns.split('.');
		for(var i = 0; i < x.length; i++) {
			o[x[i]] ? "" : o[x[i]] = {};
			o = o[x[i]];
		}
		return o;

	};

	qd.importCss = function(url) {
		var head = $("head:first");
		if(head.find('link[href="' + url + '"]').size() == 0) {
			var link = $('<link rel="stylesheet" type="text/css" href="' + url + '"/>');
			$("head:first").append(link);
		}
	};

	/**
	 * Ajax远程访问业务API
	 * @parms disable_msg_fun: 禁用消息自动处理 默认为false
	 */
	qd.rpc = function(api, params, disable_msg_fun) {
		if(!params) { params = {}; } else if(typeof params == 'function') {
			var _params = params;
			params = _params();
		}
		if(!/(\w+\.)+(\w+)?Api\.\w+/.test(api)) { throw new Error("Api pattern Error.") }
		var _ajax = $.ajax({
				type: 'POST',
				dataType: 'json',
				url: '/remote/' + api + '/',
				data: { '_params': JSON.stringify(params) }
			})
			.success(function(result) {
				if(disable_msg_fun) { return; }
				if(!(result && result.msg)) { return; }
				if(result.err == 0 && result.msg != '') { qd.notify.info(result.msg); return; }
				if(result.err >= 0 && result.msg != '') {
					qd.notify.error(result.msg);
					if(result.err == 2) { location.href = (location.href.indexOf("wy") > -1) ? "/wuye_logout/" : "/mgr_logout/"; }
				}
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
	qd.Class = function() {
		if(arguments.length == 0) {
			throw new Error("Argument error! Create new class, please writting as: Class([super], {...})");
		}
		var superCls = arguments.length == 2 ? arguments[0] : function() {};
		var newCls = function() {
			this.__super__ = superCls;
			if(this.__init__) this.__init__.apply(this, arguments);
		};
		var pros = arguments.length == 1 ? arguments[0] : arguments[1];

		for(var key in superCls.prototype) {
			newCls.prototype[key] = superCls.prototype[key];
		}

		for(var key in pros) {
			newCls.prototype[key] = pros[key];
		}

		return newCls;
	};

	qd.has_role = function(t) {
		var r = qd_x001002003789654123695;
		var v = 1;
		if(r == 'manager') { v = 2 } else if(r == 'system') { v = 3 }

		var xx = { c: 1, m: 2, s: 3 };

		return v >= (xx[t] || 100);

	};

	qd.ws = function(url, params, callback) {
		var ws = new WebSocket(url);

		ws.onmessage = function(evt) {
			callback(evt.data);
		};

		ws.onopen = function(evt) {
			Object.keys(params).forEach(function(key) {
				ws.send(key + ":" + params[key]);
			});
		};

		ws.onclose = function(evt) {
			console.log('onclose');
		};
	};

	qd.fileSizeCheck = function(target) {
		var isIE = /msie/i.test(navigator.userAgent) && !window.opera;
		var fileSize = 0,
			filetype = "",
			file_type = $(target).data('accept');
		if(isIE && !target.files) {
			var filePath = target.value;
			var fileSystem = new ActiveXObject("Scripting.FileSystemObject");
			var file = fileSystem.GetFile(filePath);
			fileSize = file.Size; // 文件大小，单位：b
		} else { // 非IE浏览器
			fileSize = target.files[0].size;
			var filename = target.files[0].name;
			if(filename) {
				filetype = filename.substr(filename.lastIndexOf(".") + 1)
			}
		}
		var size = fileSize / 1024 / 1024;
		if(size > 50) {
			qd.notify.error("文件不能大于50M");
			target.value = "";
		}

		if(file_type.indexOf(filetype) < 0) {
			qd.notify.error("文件格式错误");
			target.value = "";
		}
	}

	//-------------------------------------------------------------------------------//
	var utils = qd.utils = {};

	/**
	 * 格式化字符串
	 * 示例代码:
	 * formatStr('Hello {0}, I klie {1}','word', 'JS');
	 * >>>Hello word, I klie JS
	 */
	utils.formatStr = function() {
		var str = arguments[0];
		for(var i = 1; i < arguments.length; i++) {
			var reg = eval("(/\\{\\s*" + (i - 1) + "\\s*\\}/gi)");
			str = str.replace(reg, arguments[i]);
		}
		return str;
	};

	utils.getTimeStr = function(time, sortFormat) {
		var fm = "{0}-{1}-{2} {3}:{4}";
		if(sortFormat) { fm = "{0}-{1}-{2}"; }
		var fix0 = function(n) {
			if(n < 10) return "0" + n;
			return n + "";
		};
		if(time == 0) return "";
		if(time * 1 == NaN) return '';
		var d = new Date();
		d.setTime(time * 1);
		return utils.formatStr(fm, d.getFullYear(),
			fix0(d.getMonth() + 1), fix0(d.getDate()), fix0(d.getHours()), fix0(d.getMinutes()))
	};

	utils.val2boolean = function(val) {
		if(val == "是" || val == "yes" || val == "true") return true;
		if(val == "否" || val == "no" || val == "false") return false;

		if(val) return true;
		return false;
	}

	utils.val2booleanStr = function(val) {
		if(val == "是" || val == "yes" || val == "true") return true + "";
		if(val == "否" || val == "no" || val == "false") return false + "";
		if(val) return true + "";
		return false + "";
	}

	utils.humanize_time = function(ms) {
		ms = Math.round(ms);
		var m = Math.floor(ms / 60);
		var s = ms % 60;
		return utils.formatStr("{0}分{1}秒", m, s);

	}

	/**
	 * 删除对象属性
	 * simple: delattrs(obj, "name", "age", ...) 
	 */
	utils.delattrs = function() {
		if(arguments.length < 2) return;
		var obj = arguments[0]
		if(!obj) return;

		for(var i = 1, len = arguments.length; i < len; i++) {
			delete obj[arguments[i]];
		}
	}

	utils.Observer = function() {
		this.events = {};

		/** 触发事件  */
		this.fireEvent = function(eName) {
			var events = this.events[eName];
			if(!events) return;

			var handlerArguments = [];
			for(var i = 1; i < arguments.length; i++) {
				handlerArguments.push(arguments[i]);
			}

			for(var i = 0; i < events.length; i++) {
				var event = events[i];
				event.handler.apply(event.scope || this, handlerArguments);
			}

		};

		/** 事件绑定 */
		this.on = function(eName, handler, scope) {
			if(!this.events[eName]) this.events[eName] = [];
			this.events[eName].push({ handler: handler, scope: scope });
		};

		/** 取消事件，如果handler不存在，取消所有事件 */
		this.un = function(eName, handler) {
			var events = this.events[eName];
			if(!events || events.length == 0) return;
			if(events && !handler) {
				events.splice(0, events.length);
				return;
			}

			for(var i = events.length - 1; i >= 0; i--) {
				if(events[i].handler == handler) events.splice(i, 1);
			}
		}
	};

	//延时任务管理功能
	utils.DelayTaskMrg = {
		_tasks: {},
		_DelayTask: function(xfun) {
			//console.info('new _DelayTask...');
			this.time = 800;
			/** 执行 */
			this.excute = function() { xfun(arguments); };

			/** 
			 * 运行, 在time毫秒内再次执行此任务，上次未执行任务将被取消
			 * @note 处理函数参数在time参数后面加入
			 * @param {int} time
			 */
			this.run = function(time) {
				if(time) {
					this.time = time;
				}
				clearTimeout(this._taskTimer);
				var newArguments = [];
				for(var i = 1; i < arguments.length; i++) {
					newArguments.push(arguments[i]);
				}
				this._taskTimer = setTimeout(function() { xfun.apply({}, newArguments) }, this.time);
			}

		},
		/**
		 * 创建延时任务
		 * @param {String} id 唯一任务ID，如果id已经存在，则返回已创建的任务对象
		 * ＠param {Function} xfun 任务处理函数
		 */
		createTask: function(id, xfun) {
			if(this._tasks[id]) return this._tasks[id];
			var task = new this._DelayTask(xfun);
			this._tasks[id] = task;
			return task;
		}
	};

	utils.delayTask = function(tid, xfun, time) {
		utils.DelayTaskMrg.createTask(tid, xfun).run(time);
	}

	//-------------------------------------校验方法-----------------------------------------------------//

	utils.isEmpty = function(obj) {
		if($.type(obj) == 'string' && obj == '') { return true }
		return $.isEmptyObject(obj);

	}
	utils.isValidIp = function(ip) {
		if(ip == "255.255.255.255") return false;
		if(/^0{1,3}\.0{1,3}\.0{1,3}\.0{1,3}$/.test(ip)) return false;

		var exp = /^(?:(?:[1-9]?[0-9]|1[0-9]{2}|2(?:[0-4][0-9]|5[0-5]))\.){3}(?:[1-9]?[0-9]|1[0-9]{2}|2(?:[0-4][0-9]|5[0-5]))$/;
		if(exp.test(ip)) { return true }
		return false

	};

	utils.isValidUrl = function(ip) {
		var exp = /^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?$/;
		if(exp.test(ip)) { return true }
		return false
	};

	utils.isValidMac = function(ip) {
		var exp = /^\s*([0-9a-fA-F]{2,2}[:|-]){5,5}[0-9a-fA-F]{2,2}\s*$/;
		if(exp.test(ip)) { return true }
		return false
	};

	utils.isVaildEmail = function(email) {
		var exp = /^[0-9a-zA-Z_\.#]+@(([0-9a-zA-Z]+)[.])+[a-z]{2,4}$/;
		if(exp.test(email)) { return true }
		return false
	};

	utils.isVaildPhone = function(phone) {
		var exp1 = /^0\d{2,3}-\d{7,8}$/;
		var exp2 = /^1\d{10,10}$/;

		if(exp1.test(phone) || exp2.test(phone)) { return true; }
		return false;
	}

	utils.isValidNum = function(val) {
		var exp = /^-?\d+(\.\d+)?$/;
		if(exp.test(val)) {
			return true
		}
		return false
	}

	//--------------------------------------------------------------------------------------//

	/**
	 * trim 对象属性的空格，只对字符类型的属性有效
	 * @param {Object} obj
	 * @param {Object} pns 可选参数，属性名列表
	 */
	utils.trimObj = function(obj, pns) {
		$.each(obj, function(key, value) {
			if(typeof value !== 'string') return;
			if(!pns || pns.length == 0) {
				obj[key] = $.trim(value);
			} else if($.inArray(key, pns) >= 0) {
				obj[key] = $.trim(value);
			}
		});
	};

	utils.fillSelect = function(el, data, options) {
		var _options = { default_value: "", default_label: '-- 选择 --' };
		$.extend(_options, options);
		$(el).html('');
		$(el).append(utils.formatStr('<option value="{0}">{1}</option>', _options.default_value, _options.default_label));
		$.each(data, function(i, item) {
			var option_value = eval('item' + _options['value']);
			var option_label = eval('item' + _options['label']);
			$(el).append(utils.formatStr('<option value="{0}">{1}</option>', option_value, option_label));
		});

	};

	utils.serialize = function(el) {
		var serialize_obj = {};
		$(el).find(':hidden, :text, input[type=number], :password, textarea, select, :checkbox:checked, :radio:checked').each(function() {
			var name = $.trim($(this).attr('name') || "");
			var value = $.trim($(this).val() || "");
			if(name == '') {
				return;
			}
			if(/^(\w+)\.(\w+)$/.test(name)) {
				if(!serialize_obj[RegExp.$1]) { serialize_obj[RegExp.$1] = {} }
				serialize_obj[RegExp.$1][RegExp.$2] = value;
			} else {
				serialize_obj[name] = value;
			}
		});

		return serialize_obj;
	}

	qd.notify = {
		success: function(msg) {
			$('.notifications').notify({ type: 'success', message: msg }).show();
		},
		info: function(msg) {
			$('.notifications').notify({ type: 'info', message: msg }).show();
		},
		error: function(msg) {
			$('.notifications').notify({ type: 'danger', message: msg }).show();
		}
	};

	qd.mk_pagination = function(pagination, page_size_bar) {
		if(!pagination) return '';
		var template = $('script[name=pagination_template]').html();

		var compiled = _.template(template);
		return compiled({ pagination: pagination, page_size_bar: !!page_size_bar });

	}

	qd.render_template = function(tmp_name, data, container) {
		var template = $('script[name=' + tmp_name + '_template]').html();
		var compiled = _.template(template);
		var html = compiled(data);

		if(container) {
			$(container).html('').html(html);
		}

		return html;
	};

	$.fn.extend({
		/**
		 * 把数据渲染到指定的模板中
		 * @param data
		 * @param tmp_name, 可选参数, 可以在container el 的data中指定
		 */
		render_template: function(data, tmp_name) {
			if(!tmp_name || tmp_name == "") { tmp_name = this.data('template'); }
			if(!tmp_name || tmp_name == "") { throw new Error("Template name is not valid.") }
			qd.render_template(tmp_name, data, this);
		}
	});

	qd.load_view_tpls = function(url) {
		$.ajax({
			url: url,
			async: false,
			success: function(html) {
				$("#view_templates").html(html);
			}

		});
	};
	qd.qd_layui = function(res,id) {
		var list = [];
		var result = res;
		for(var i = 0; i < result.data.collection.length; i++) {
			var collection = result.data.collection;
			list[i] = {}
			list[i].name = collection[i].name
			list[i].checkboxValue = collection[i]._id;
			list[i].checked = false;
			list[i].spread = false;
			list[i].children = [];
			for(var j = 0; j < collection[i].childs.length; j++) {
				list[i].children[j] = {}
				var childs = collection[i].childs;
				list[i].children[j].name = childs[j].name;
				list[i].children[j].checkboxValue = childs[j]._id;
				list[i].children[j].checked = false;
				list[i].children[j].children = [];
				for(var a = 0; a < childs[j].projects.length; a++) {
					list[i].children[j].children[a] = {};
					var projects = childs[j].projects;
					list[i].children[j].children[a].name = projects[a].name;
					list[i].children[j].children[a].checkboxValue = projects[a].id;
					list[i].children[j].children[a].checked = false;
				}
			}
		}
		layui.use('tree', function() {
			var tree = layui.tree({
				elem: id, //指定元素，生成的树放到哪个元素上
				check: 'checkbox', //勾选风格
				skin: 'as', //设定皮肤
				drag: false, //点击每一项时是否生成提示信息
				checkboxName: 'aa[]', //复选框的name属性值
				checkboxStyle: "", //设置复选框的样式，必须为字符串，css样式怎么写就怎么写
				click: function(item) { //点击节点回调
					console.log(item)
				},
				nodes: list
			});
			//生成一个模拟树
			var createTree = function(node, start) {
				node = node || function() {
					var arr = [];
					for(var i = 1; i < 10; i++) {
						arr.push({
							name: i.toString().replace(/(\d)/, '$1$1$1$1$1$1$1$1$1')
						});
					}
					return arr;
				}();
				start = start || 1;
				layui.each(node, function(index, item) {
					if(start < 10 && index < 9) {
						var child = [{
							name: (1 + index + start).toString().replace(/(\d)/, '$1$1$1$1$1$1$1$1$1')
						}];
						node[index].children = child;
						createTree(child, index + start + 1);
					}
				});
				return node;
			};
		});
	}

})(jQuery);