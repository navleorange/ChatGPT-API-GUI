from django.http import StreamingHttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from api.lib import util
from api.lib.chatgpt import ChatGPT

config_path = "./api/res/config.ini"
inifile = util.load_config(config_path=config_path)
inifile.read(config_path,"UTF-8")
chatgpt = ChatGPT(inifile=inifile)

class ApiView(TemplateView):
    template_name = "gui/index.html"

    def get(self, request, **kwargs):
        params = {"message":"Hello!!!"}
        return self.render_to_response(params)
    
    def stream_render(self, request, message:str):
        for _ in chatgpt.create_comment_stream(text=message):
            params = {"message_list": chatgpt.talk_history}
            print(params)
            yield loader.render_to_string(ApiView.template_name, params, request)
    
    def post(self, request, **kwarg):
        message = request.POST["message"]

        for _ in chatgpt.create_comment_stream(text=message):
            params = {"message_list": chatgpt.talk_history}
            #yield render(request, "gui/index.html", params)
        
        return self.render_to_response(params)

        # response = StreamingHttpResponse(self.stream_render(request,message))
        # return response