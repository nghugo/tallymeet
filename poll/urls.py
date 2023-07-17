from django.urls import path
from . import views
from .views import PollCreateView, PollDetailView

urlpatterns = [
    path("", views.home, name="poll-home"),
    path("base/", views.base, name="poll-base"),  # for debugging
    path("happy/", views.happy, name="poll-happy"),  # for debugging
    path("poll/create/", PollCreateView.as_view(), name="poll-create"),
    path("poll/detail/<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
]