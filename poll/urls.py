from django.urls import path
from . import views
from .views import PollCreateView, PollDetailView , PollUpdateView, PollUpdatePasswordView, PollDeleteView

urlpatterns = [
    path("", views.home, name="poll-home"),
    path("base/", views.base, name="poll-base"),  # for debugging
    path("poll/password/", views.poll_verify_password, name="poll-verify-password"),
    path("poll/password_rwpid/", views.poll_verify_password_redirect_with_poll_id, name="poll-verify-password-redir-wpid"),
    
    path("poll/create/", PollCreateView.as_view(), name="poll-create"),
    path("poll/detail/<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("poll/update/<int:pk>/", PollUpdateView.as_view(), name="poll-update"),
    path("poll/update_password/<int:pk>/", PollUpdatePasswordView.as_view(), name="poll-update-password"),
    path("poll/delete/<int:pk>/", PollDeleteView.as_view(), name="poll-delete"),
]