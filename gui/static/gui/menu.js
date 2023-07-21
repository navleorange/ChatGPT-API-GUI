$(function(){
	var menu_button = document.querySelector("#model_menu_button")

	menu_button.addEventListener("click",() => {
		$("#settings_list").animate({"width":"toggle"})
		menu_button.classList.toggle("settings-open")

		if($("#model_menu_button").hasClass("settings-open")){
			menu_button.textContent = ">>"
		}
		else{
			menu_button.textContent = "<<"
		}

	});

});