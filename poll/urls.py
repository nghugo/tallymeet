from django.urls import path
from . import views
from .views import (home, poll_verify_password, poll_verify_password_redirect_with_poll_id, 
                    PollCreateView, PollDetailView , PollUpdateView, 
                    PollUpdatePasswordView, PollDeleteView, vote)

urlpatterns = [
    # path("base/", views.base, name="poll-base"),  # for debugging
    path("", home, name="poll-home"),
    path("poll/password/", poll_verify_password, name="poll-verify-password"),
    path("poll/password_rwpid/", poll_verify_password_redirect_with_poll_id, name="poll-verify-password-redir-wpid"),
    
    path("poll/create/", PollCreateView.as_view(), name="poll-create"),
    path("poll/detail/<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("poll/update/<int:pk>/", PollUpdateView.as_view(), name="poll-update"),
    path("poll/password_update/<int:pk>/", PollUpdatePasswordView.as_view(), name="poll-update-password"),
    path("poll/delete/<int:pk>/", PollDeleteView.as_view(), name="poll-delete"),

    path("poll/vote/<int:pk>/", vote, name="poll-vote"),

]