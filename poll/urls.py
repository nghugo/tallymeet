from django.urls import path
from . import views

urlpatterns = [
    path("base/", views.base, name="poll-base"),
    path("happy/", views.happy, name="poll-happy"),
    path("", views.home, name="poll-home")
]