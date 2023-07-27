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

function setting_content_click(radio_elems, setting_elems, elem_index){
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
			$("#model_detail").toggle();
		}
		else{
			// number detail
			$("#number_detail").toggle();
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
						"Chat-Update-Target":"MODEL",
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

function setting_detail_click(){
	return function(){
	}
};

function back_content_button_click(setting_elems){
	return function(){

		for(var i=0; i<setting_elems.length; i++){

			if($("#"+setting_elems[i]).css("display") == "none"){
				$("#"+setting_elems[i]).toggle()
			}
		}

		$(".setting_content").toggle();
		$(".setting_detail").toggle();

		if($("#model_detail").css("display") == "none"){
			$("#number_detail").toggle();
		}
		else{
			$("#model_detail").toggle();
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
	for(var i=0; i<setting_elems.length; i++){
		document.getElementById(setting_elems[i]).addEventListener("click",setting_content_click(radio_elems,setting_elems,i));
	}

	// setting detail event
	var model_detail = document.querySelector("#model_detail")
	model_detail.addEventListener("click",model_detail_click())

	var back_content_button = document.querySelector("#back_content")
	back_content_button.addEventListener("click",back_content_button_click(setting_elems))

	$(".message_input_footer").submit();
});