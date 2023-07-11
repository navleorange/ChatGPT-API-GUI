from django.shortcuts import render

def index(request):
    params = {"message":"Hello!!!"}
    return render(request, "gui/index.html", context=params)

def form(request):
    message = request.POST["message"]
    params = {"message": message}

    return render(request, "gui/index.html", params)