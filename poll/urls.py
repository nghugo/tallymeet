from django.urls import path
from . import views
from .views import PollCreateView

urlpatterns = [
    path("", views.home, name="poll-home"),
    path("poll/create/", PollCreateView.as_view(), name="poll-create"),
    # path("base/", views.base, name="poll-base"),  # for debugging
    # path("happy/", views.happy, name="poll-happy"),  # for debugging
]