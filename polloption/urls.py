from django.urls import path
from .views import pollOptionEdit

urlpatterns = [
    path("edit/", pollOptionEdit, name="poll-option-edit"),
]


