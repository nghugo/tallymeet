from django.urls import path
from . import views

urlpatterns = [
    path("base/", views.base, name="poll-base"),
    path("", views.home, name="poll-home")
]