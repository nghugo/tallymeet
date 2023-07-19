from django.urls import path
from . import views
from .views import PollOptionCreateView

urlpatterns = [
    path("create/", PollOptionCreateView.as_view(), name="poll-optioncreate"),
]