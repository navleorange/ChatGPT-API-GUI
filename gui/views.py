from typing import Any
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
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

    def ajax_response(self, message):
        # return HttpResponse(chatgpt.test_create(text=message))
        return StreamingHttpResponse(chatgpt.create_comment_stream(text=message))
    
    def post(self, request, **kwarg):
        message = request.POST["message"]

        return self.ajax_response(message=message)