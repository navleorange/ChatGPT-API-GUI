function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }   
    return cookieValue;
}

function setDoubleQuote(text){
	return "\"" + text + "\""
}

function makeMessageParagraph(role, index, message){
	return "<p class=" + setDoubleQuote(role) + "id=" + setDoubleQuote(role + index) + ">" + message + "</p>"
}

$(function(){
	$(".message_input_footer").submit(function(event){
		event.preventDefault();

		// chatgpt role setting
		var user_role = "user"
		var assistant_role = "assistant"

		// add user message
		var user_message_num = document.querySelectorAll(".user").length;
		var user_message = $("#message_input").val();

		// avoid null
		if(!user_message || user_message.length == 0){
			return
		}

		$(".conversation").append(makeMessageParagraph(user_role,user_message_num+1,user_message));

		// send user message to server and receive chatgpt message
		var form = $(this);
		var ajax_chatgpt = new XMLHttpRequest();
		ajax_chatgpt.onreadystatechange = function(){
			if(ajax_chatgpt.readyState != 4){
				// lock button
				var button = document.getElementById("send_button")
				button.setAttribute("disabled",true)
			}
			if(ajax_chatgpt.readyState == 3){
				// append new text
				var text_processing = ajax_chatgpt.responseText.split("}}") 			// separate messages
				text_processing = text_processing.filter(element => !(element==""));	// remove space
				var display_text = text_processing[text_processing.length - 1] + "}}";	// pick up latest message
				display_text = display_text.replace(/\'/g,"\"");						// replace ' -> "
				display_text = JSON.parse(display_text);								// text to json

				if(document.getElementById(assistant_role + display_text.index) != null && document.getElementById(assistant_role + display_text.index).textContent.length < display_text.message.content.length){	// find_index and prev_text_length < current_text_length
					document.getElementById(assistant_role + display_text.index).remove();
					$(".conversation").append(makeMessageParagraph(assistant_role,display_text.index,display_text.message.content));
				}
				else{
					$(".conversation").append(makeMessageParagraph(assistant_role,display_text.index,display_text.message.content));
				}

			}
			else if(ajax_chatgpt.readyState == 4){
				var text_processing = ajax_chatgpt.responseText.split("}}") 			// separate messages
				text_processing = text_processing.filter(element => !(element==""));	// remove space
				var display_text = text_processing[text_processing.length - 1] + "}}";	// pick up latest message
				display_text = display_text.replace(/\'/g,"\"");						// replace ' -> "
				display_text = JSON.parse(display_text);								// text to json

				// if display is not complated append
				if(document.getElementById(assistant_role + display_text.index) != null && document.getElementById(assistant_role + display_text.index).textContent.length < display_text.message.content.length){	// find_index and prev_text_length < current_text_length
					document.getElementById(assistant_role + display_text.index).remove();
					$(".conversation").append(makeMessageParagraph(assistant_role,display_text.index,display_text.message.content));
				}

				// release button
				var button = document.getElementById("send_button")
				button.removeAttribute("disabled")
			}

			// scroll
			var chatgpt_messages = document.querySelectorAll(".assistant")
			var elem = chatgpt_messages[chatgpt_messages.length - 1]
			elem.scrollIntoView({
				block: "center",
				inline: "nearest",
				behavior: "smooth",
			})

		};

		console.log("---------------form------------------")
		console.log(form)

		// url: form.prop('action') method: form.prop('method')
		ajax_chatgpt.open(form.prop('method'), form.prop('action'));

		// ヘッダにCSRFトークンをセットする。
		const csrftoken = getCookie('csrftoken');
		ajax_chatgpt.setRequestHeader("X-CSRFToken", csrftoken);

		// set header
		ajax_chatgpt.setRequestHeader("X-Requested-With", "XMLHttpRequest");

		// dataType: 'text'
		ajax_chatgpt.responseType = "text";

		// data: form.serialize()
		form =  document.querySelector(".message_input_footer");
		data = new FormData(form)
		ajax_chatgpt.send(data);

	});
});