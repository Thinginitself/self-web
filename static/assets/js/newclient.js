function jump_list(environment_name) {
    location = 'environment_list?environment_name='+environment_name;
}

function add_res() {
    if (input_res_name.value == "") {
        return;
    }
    var del_res_data = {
        "del_res_name": input_res_name.value
    };
    $.post("/del_res", del_res_data);
    var new_res_data = {
    	"res_environment": res_environment.innerText,
        "res_name": input_res_name.value,
        "res_format": input_res_format.value,
        "res_initial": input_res_initial.value,
        "res_delay": input_res_delay.value,
        "res_next": input_res_next.value,
        "res_rule": input_res_rule.value
    };

    $.post("/add_res", new_res_data, jump_list(res_environment.innerText));
}

function del_res(del_res_name, environment_name) {
    var del_res_data = {
        "del_res_name": del_res_name
    };
    $.post("/del_res", del_res_data, jump_list(environment_name));
}

function custom_res(res_name, res_environment) {
    location = 'environment_custom?res_name='+res_name+'&res_environment='+res_environment;
}

function load_environment(){
	checklist = document.getElementsByClassName("check");
	for (var i = checklist.length - 1; i >= 0; i--) {
		if (checklist[i].checked == true) {
			$.post('/set_environment',{"environment_name":checklist[i].for})
		}
	}
	location = 'runtime_main';
}
