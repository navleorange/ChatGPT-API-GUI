from django.http import StreamingHttpResponse
from django.views.generic import TemplateView
from api.lib import util
from api.lib.chatgpt import ChatGPT

config_path = "./api/res/config.ini"
inifile = util.load_config(config_path=config_path)
inifile.read(config_path,"UTF-8")
chatgpt = None

class ApiView(TemplateView):
    template_name = "gui/index.html"

    def get(self, request, **kwargs):
        params = {"message":"Hello!!!",
                  "log_title_list":util.get_log_list(log_path=inifile.get("log","path"))}
        print(params)
        return self.render_to_response(params)

    def ajax_response(self, message):
        # return HttpResponse(chatgpt.test_create(text=message))
        return StreamingHttpResponse(chatgpt.create_comment_stream(text=message))
    
    def post(self, request, **kwarg):
        global chatgpt
        message = request.POST["message"]

        if chatgpt == None: chatgpt= ChatGPT(inifile=inifile,title=message)

        return self.ajax_response(message=message)