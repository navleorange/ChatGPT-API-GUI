from django.urls import path

from . import views

urlpatterns = [
    path("",views.ApiView.as_view(),name="index"),
    path("/form",views.ApiView.as_view(),name="form")
]