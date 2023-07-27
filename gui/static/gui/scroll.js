$(function(){
	var user_messages = document.querySelectorAll(".user")
	var chatgpt_messages = document.querySelectorAll(".assistant")

	var elem = user_messages[user_messages.length - 1]

	if (chatgpt_messages.length >= user_messages.length){
		elem = chatgpt_messages[chatgpt_messages.length - 1]
	}

	// scroll detail
	if(elem != null){
		elem.scrollIntoView({
			block: "center",
			inline: "nearest",
			behavior: "smooth",
		})
	}

});