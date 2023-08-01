function display_setting_menu(menu_button){
	return function(){
		$("#settings_list").animate({"width":"toggle"})
		menu_button.classList.toggle("settings-open")

		if($("#model_menu_button").hasClass("settings-open")){
			menu_button.textContent = ">>"
		}
		else{
			menu_button.textContent = "<<"
		}
	}
};

function get_target_detail(setting_elems){
	var target = ""
	for(var i=0; i<setting_elems.length; i++){

		if($("#"+setting_elems[i]).css("display") != "none"){
			target = setting_elems[i]
		}
	}

	return target
}

function toggle_attribute(target_id, attribute, value){
	var target = document.getElementById(target_id);
	target.hasAttribute(attribute) ? target.removeAttribute(attribute) : target.setAttribute(attribute,value);
}

function toggle_value(target_id, ref_id){
	var value = "value"
	var target = document.getElementById(target_id);

	if(target.hasAttribute(value)){
		target.removeAttribute(value)
	}
	else{
		var ref_num = document.getElementById(ref_id).textContent
		ref_num = ref_num.match(/\./g) ? parseFloat(ref_num).toFixed(2) : Number(ref_num)
		target.setAttribute("value",ref_num);
		target.value = ref_num
	}
}

function setting_content_click(radio_elems, setting_elems, elem_index, model_detail_id, numerical_detail_id){
	return function(){

		// setting_content_title display:block -> display:none or display:none -> display:block
		for(var i=0; i<setting_elems.length; i++){
			if(i == elem_index){
				continue;
			}
			$("#"+setting_elems[i]).toggle();
		}

		// setting_content display:block -> display:none or display:none -> display:block
		$(".setting_content").toggle();
		$(".setting_detail").toggle();

		if(radio_elems.includes(setting_elems[elem_index])){
			// model detail
			$(model_detail_id).toggle();
		}
		else{
			// numerical detail
			$(numerical_detail_id).toggle();

			var target = setting_elems[elem_index]

			for(var detail in numerical_params[target]){
				toggle_attribute("numerical_detail_input",detail,numerical_params[target][detail])
			}

			toggle_value("numerical_detail_input",setting_elems[elem_index] + "_content")
		}

	}
};

function model_detail_click(){
	return function(){
		var model_list = document.getElementsByName("model_name");
		var next_model = ""
		var next_index = -1

		for(var i=0; i<model_list.length; i++){
			if(model_list.item(i).checked){
				next_model = model_list.item(i).value
				next_index = i
			}
		}

		data = {"model":next_model}

		$.ajax({
			url: "",
			type: "PUT",
			headers: { "X-CSRFToken":  getCookie('csrftoken'),
						"Chat-Update-Target":"Model",
		},
			data: data,
			dataType: "text",
		})
		.done(function(data){
			model_list[next_index].checked = true;
			var model_content = document.getElementById("model_content")
			model_content.innerText = next_model
		})

	}
};

function change_numerical_click(setting_elems){
	return function(){
		var target = ""

		for(var i=0; i<setting_elems.length; i++){

			if($("#"+setting_elems[i]).css("display") != "none"){
				target = setting_elems[i]
			}
		}

		var ref_num = document.getElementById("numerical_detail_input").value
		ref_num = ref_num.match(/\./g) ? parseFloat(ref_num).toFixed(2) : Number(ref_num)
		var data = {}
		data[target] = ref_num

		$.ajax({
			url: "",
			type: "PUT",
			headers: { "X-CSRFToken":  getCookie('csrftoken'),
						"Chat-Update-Target": "NumericalValue"},
			data: data,
			dataType: "text",
		})
		.done(function(){
			var model_content = document.getElementById(target + "_content")
			model_content.innerText = ref_num
		})
	}
};

function back_content_button_click(setting_elems, radio_elems, model_detail_id, numerical_detail_id){
	return function(){

		for(var i=0; i<setting_elems.length; i++){

			if($("#"+setting_elems[i]).css("display") == "none"){
				$("#"+setting_elems[i]).toggle()
			}
			else if(!radio_elems.includes(setting_elems[i])){
				var target = setting_elems[i]
				for(var detail in numerical_params[target]){
					toggle_attribute("numerical_detail_input",detail,numerical_params[target][detail])
				}
				toggle_value("numerical_detail_input",setting_elems[i] + "_content")
			}
		}

		$(".setting_content").toggle();
		$(".setting_detail").toggle();

		if($(model_detail_id).css("display") == "none"){
			$(numerical_detail_id).toggle();
		}
		else{
			$(model_detail_id).toggle();
		}
	}
}

$(function(){

	// setting list event
	var menu_button = document.querySelector("#model_menu_button")
	menu_button.addEventListener("click",display_setting_menu(menu_button));

	// setting content event
	var setting_elems = ["model","temperature","top_p","generate_num","max_tokens","presence_penalty","frequency_penalty"]
	var radio_elems = ["model"]
	model_detail_id = "#model_detail"
	numerical_detail_id = "#numerical_detail"

	for(var i=0; i<setting_elems.length; i++){
		document.getElementById(setting_elems[i]).addEventListener("click",setting_content_click(radio_elems,setting_elems,i,model_detail_id,numerical_detail_id));
	}

	// setting detail event

	// model detail
	var model_detail = document.querySelector(model_detail_id)
	model_detail.addEventListener("click",model_detail_click())

	// number detail
	var numerical_detail = document.querySelector(numerical_detail_id)
	numerical_detail.addEventListener("click",change_numerical_click(setting_elems))

	// back content button
	var back_content_button = document.querySelector("#back_content")
	back_content_button.addEventListener("click",back_content_button_click(setting_elems,radio_elems,model_detail_id,numerical_detail_id))
});