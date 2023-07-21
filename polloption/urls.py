from django.urls import path
from . import views
from .views import pollOptionCreate, PollOptionDetailView

urlpatterns = [
    path("create/", pollOptionCreate, name="poll-option-create"),
    # path("create/", PollOptionCreateView.as_view(), name="poll-option-create"),
    path("poll/detail/<int:pk>/", PollOptionDetailView.as_view(), name="poll-option-detail"),
]

