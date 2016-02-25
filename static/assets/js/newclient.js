function add_res(){
	var new_res_data = {"res_name":input_res_name.value,
						"res_format":input_res_format.value,
						"res_initial":input_res_initial.value,
						"res_delay":input_res_delay.value,
						"res_next":input_res_next.value,
						"res_rule":input_res_rule.value};

	$.post("/add_res", new_res_data,function(){window.location.href='environment_list';});
	
}