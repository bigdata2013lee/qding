(function($) {

	$.fn.extend({
		qd_phase_build_select: function(query_back) {
			var inst = this;
			//var phase_empty_label = "-- Please Select Phase --";
			// var building_empty_label = "-- Please Select Building --";

			var phase_empty_label = "全部 ";
			var building_empty_label = "全部 ";

			var phase_select = this.find("select[name=phase_id]");
			phase_select.html('<option value="">' + phase_empty_label + '</option>');

			var building_select = this.find("select[name=building_id]");
			building_select.html('<option value="">' + building_empty_label + '</option>');

			qd.rpc("aptm.AptmQueryApi.list_phases", { project_id: select_project_id }).success(function(result) {
				var collection = result.data.collection || [];
				$.each(collection, function(i, o) {
					phase_select.append('<option value="' + o.id + '">' + o.name + '</option>');
				})
			});

			var list_buildings = function(phase_id) {
				building_select.html('<option value="">' + building_empty_label + '</option>');
				qd.rpc("aptm.AptmQueryApi.list_buildings", { phase_id: phase_id }).success(function(result) {
					var collection = result.data.collection || [];
					$.each(collection, function(i, o) {
						building_select.append('<option value="' + o.id + '">' + o.name + '</option>');

					})
				});
			};

			this.delegate("select[name=phase_id]", 'change', function(evt) {
				building_select.html('<option value="">' + building_empty_label + '</option>');
				var val = inst.find("select[name=phase_id]").val();
				if(val == "") {
					return;
				}
				list_buildings(val);
			});

			this.delegate("select[name=building_id]", 'change', function(evt) {
				// console.info("Exec  query action");
			})

		},
		qd_province_city_select: function(url) {
			var inst = this;

			var p_empty_label = "-- 请选择省份 --";
			var c_empty_label = "-- 请选择城市 --";

			var p_select = this.find("select[name=pcity_id]");
			p_select.html('<option value="">' + p_empty_label + '</option>');

			var c_select = this.find("select[name=ccity_id]");
			c_select.html('<option value="">' + c_empty_label + '</option>');

			var _collection = [];
			qd.rpc(url, {}).success(function(result) {
				_collection = result.data.collection || [];
				$.each(_collection, function(i, o) {
					p_select.append('<option value="' + o._id + '">' + o.name + '</option>');
				})
			});

			var city_init = function(pid) {
				$.each(_collection, function(i, o) {
					if(o._id == pid) {
						$.each(o.childs, function(index, item) {
							c_select.append('<option value="' + item._id + '">' + item.name + '</option>');
						})
					}
				});
			};

			this.delegate("select[name=pcity_id]", 'change', function(evt) {
				c_select.html('<option value="">' + c_empty_label + '</option>');
				var val = inst.find("select[name=pcity_id]").val();
				if(val == "") {
					return;
				}
				city_init(val);
			});
		}
	});
})(jQuery);