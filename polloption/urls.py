from django.urls import path
from .views import pollOptionEdit, pollOptionCreate, PollOptionDeleteView, pollOptionDeleteList

urlpatterns = [
    path("edit/", pollOptionEdit, name="poll-option-edit"),
    path("create/", pollOptionCreate, name="poll-option-create"),
    path("deletelist/", pollOptionDeleteList, name="poll-option-delete-list"),
    path("delete/<int:pk>/", PollOptionDeleteView.as_view(), name="poll-option-delete"),
]


