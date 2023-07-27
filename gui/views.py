from django.http import HttpResponse, StreamingHttpResponse, QueryDict
from django.views.generic import TemplateView
from api.lib import util
from api.lib.chatgpt import ChatGPT

# 別の場所に移したいけどとりあえず...
config_path = "./res/config.ini"
inifile = util.load_config(config_path=config_path)
inifile.read(config_path,"UTF-8")
chatgpt = None
past_messages = []

class ApiView(TemplateView):
    template_name = "gui/index.html"

    def get(self, request, **kwargs):
        global chatgpt, past_messages

        chatgpt= ChatGPT(inifile=inifile)
        past_messages.clear()

        params = {"message":"Hello!!!",
                    "model_data":chatgpt.get_model_data(),
                    "log_title_list":util.get_log_name(log_list=util.get_log_list(log_path=inifile.get("log","path"))),
                    "past_messages":past_messages,
                    "model_list":util.get_model_list(inifile=inifile),
                  }
        
        return self.render_to_response(params)

    def ajax_response(self, message):
        # return HttpResponse(chatgpt.test_create(text=message))
        return StreamingHttpResponse(chatgpt.create_comment_stream(text=message))
    
    def post(self, request, **kwarg):
        global chatgpt, past_messages

        if chatgpt == None: chatgpt= ChatGPT(inifile=inifile)

        # message event
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.headers.get('Chat-Update-Target') == "Message":
            message = request.POST["message"]
            return self.ajax_response(message=message)
        
        # button event
        if util.is_new_log_button_event(request=request.POST):
            past_messages.clear()
            chatgpt.clear_logger()
            chatgpt.clear_history()
            chatgpt.reset_model()
        elif util.is_log_button_event(request=request.POST):
            display_log_index = util.get_display_log_index(request=request.POST)
            past_messages = util.get_past_messages(log_path=inifile.get("log","path"), display_log_index=display_log_index)
            chatgpt.load_history(log_path=inifile.get("log","path"), display_log_index=display_log_index)

        params = {"message":"Hello!!!",
                  "model_data":chatgpt.get_model_data(),
                  "log_title_list":util.get_log_name(log_list=util.get_log_list(log_path=inifile.get("log","path"))),
                  "past_messages":past_messages,
                  "model_list":util.get_model_list(inifile=inifile),
                }
        
        return self.render_to_response(params)
    
    def model_update(self, message):
        chatgpt.change_model(model_name=message)
        return HttpResponse(status=200)
    
    def put(self, request, **kwarg):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.headers.get('Chat-Update-Target') == "MODEL":
            params = QueryDict(request.body)
            return self.model_update(message=params["model"])