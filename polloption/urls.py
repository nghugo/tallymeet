from django.urls import path
from .views import pollOptionEdit, PollOptionCreateView, PollOptionDeleteView

urlpatterns = [
    path("edit/", pollOptionEdit, name="poll-option-edit"),
    path("create/", PollOptionCreateView.as_view(), name="poll-option-create"),
    path("delete/<int:pk>/", PollOptionDeleteView.as_view(), name="poll-option-delete"),
]


